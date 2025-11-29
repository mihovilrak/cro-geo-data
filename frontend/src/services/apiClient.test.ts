jest.mock('axios', () => {
  const mockGet = jest.fn();
  const mockInstance = { get: mockGet };
  return {
    __esModule: true,
    default: {
      create: jest.fn(() => mockInstance),
      get: mockGet,
    },
  };
});

import apiClient, {
  fetchCadastralParcels,
  fetchCounties,
  fetchMunicipalities,
  fetchSettlements,
  fetchStreets,
  fetchAddresses,
  fetchLayerCatalog
} from './apiClient';

describe('apiClient', () => {
  const getMockGet = () => (apiClient as any).get as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchCadastralParcels', () => {
    it('should fetch cadastral parcels without parameters', async () => {
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      const result = await fetchCadastralParcels();

      expect(mockGet).toHaveBeenCalledWith('/cadastral_parcels/', { params: {} });
      expect(result).toEqual(mockData);
    });

    it('should fetch cadastral parcels with bbox parameter', async () => {
      const bbox: [number, number, number, number] = [100, 200, 300, 400];
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      await fetchCadastralParcels(bbox);

      expect(mockGet).toHaveBeenCalledWith('/cadastral_parcels/', {
        params: { bbox: '100,200,300,400' },
      });
    });

    it('should fetch cadastral parcels with filters', async () => {
      const filters = { municipality: 'Zagreb' };
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      await fetchCadastralParcels(undefined, filters);

      expect(mockGet).toHaveBeenCalledWith('/cadastral_parcels/', {
        params: filters,
      });
    });
  });

  describe('fetchCounties', () => {
    it('should fetch counties', async () => {
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      const result = await fetchCounties();

      expect(mockGet).toHaveBeenCalledWith('/counties/', { params: {} });
      expect(result).toEqual(mockData);
    });
  });

  describe('fetchMunicipalities', () => {
    it('should fetch municipalities', async () => {
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      const result = await fetchMunicipalities();

      expect(mockGet).toHaveBeenCalledWith('/municipalities/', { params: {} });
      expect(result).toEqual(mockData);
    });
  });

  describe('fetchLayerCatalog', () => {
    it('should fetch layer catalog', async () => {
      const mockLayers = [{ id: 'cadastral_parcels' }];
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockLayers });

      const result = await fetchLayerCatalog();

      expect(mockGet).toHaveBeenCalledWith('/layers/');
      expect(result).toEqual(mockLayers);
    });
  });

  describe('apiClient configuration', () => {
    it('should create axios instance', () => {
      expect(apiClient).toBeDefined();
    });
  });
});
