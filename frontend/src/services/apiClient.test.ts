// Note: apiClient creates axios instance at module load, so we need to mock before import
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

import apiClient, { fetchParcels, fetchAdminBoundaries, fetchLayerCatalog } from './apiClient';

describe('apiClient', () => {
  // Get the mock get function from apiClient (which is the created instance)
  const getMockGet = () => (apiClient as any).get as jest.Mock;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchParcels', () => {
    it('should fetch parcels without parameters', async () => {
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      const result = await fetchParcels();
      
      expect(mockGet).toHaveBeenCalledWith('/parcels/', { params: {} });
      expect(result).toEqual(mockData);
    });

    it('should fetch parcels with bbox parameter', async () => {
      const bbox: [number, number, number, number] = [100, 200, 300, 400];
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      await fetchParcels(bbox);
      
      expect(mockGet).toHaveBeenCalledWith('/parcels/', {
        params: { bbox: '100,200,300,400' },
      });
    });

    it('should fetch parcels with filters', async () => {
      const filters = { municipality: 'Zagreb' };
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      await fetchParcels(undefined, filters);
      
      expect(mockGet).toHaveBeenCalledWith('/parcels/', {
        params: filters,
      });
    });

    it('should fetch parcels with both bbox and filters', async () => {
      const bbox: [number, number, number, number] = [100, 200, 300, 400];
      const filters = { municipality: 'Zagreb' };
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      await fetchParcels(bbox, filters);
      
      expect(mockGet).toHaveBeenCalledWith('/parcels/', {
        params: { bbox: '100,200,300,400', ...filters },
      });
    });
  });

  describe('fetchAdminBoundaries', () => {
    it('should fetch admin boundaries', async () => {
      const mockData = { results: [] };
      const mockGet = getMockGet();
      mockGet.mockResolvedValue({ data: mockData });

      const result = await fetchAdminBoundaries();
      
      expect(mockGet).toHaveBeenCalledWith('/admin_boundaries/');
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
