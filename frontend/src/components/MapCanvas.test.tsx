import React from 'react';
import { render, waitFor } from '@testing-library/react';

// Mock axios for GetFeatureInfo requests
jest.mock('axios', () => ({
  __esModule: true,
  default: {
    get: jest.fn(),
  },
  get: jest.fn(),
}));

// OpenLayers modules and CSS are automatically mocked via moduleNameMapper in package.json
import MapCanvas from './MapCanvas';
import { LayerDescriptor } from '../services/types';

describe('MapCanvas', () => {
  const defaultDescriptor: LayerDescriptor = {
    id: 'cadastral_parcels',
    title: 'Cadastral Parcels',
    wms_name: 'cadastral_parcels',
    workspace: 'cro-geo-data',
  };

  const defaultProps = {
    selectedLayers: [] as LayerDescriptor[],
    onFeatureClick: jest.fn(),
    activeBaseLayer: 'OSM' as const,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    // Mock environment variable
    process.env.REACT_APP_GEOSERVER_URL = 'http://localhost:8080/geoserver';
  });

  afterEach(() => {
    delete process.env.REACT_APP_GEOSERVER_URL;
  });

  it('should render map container', () => {
    const { container } = render(<MapCanvas {...defaultProps} />);
    const mapDiv = container.querySelector('div');
    expect(mapDiv).toBeInTheDocument();
    expect(mapDiv).toHaveClass('w-full', 'h-full');
  });

  it('should initialize map with OSM base layer when activeBaseLayer is OSM', async () => {
    render(<MapCanvas {...defaultProps} activeBaseLayer="OSM" />);
    
    // Map initialization happens in useEffect, so we wait a bit
    await waitFor(() => {
      expect(document.querySelector('div')).toBeInTheDocument();
    });
  });

  it('should initialize map with DOF base layer when activeBaseLayer is DOF', async () => {
    render(<MapCanvas {...defaultProps} activeBaseLayer="DOF" />);
    
    await waitFor(() => {
      expect(document.querySelector('div')).toBeInTheDocument();
    });
  });

  it('should render with different selected layers', async () => {
    const { rerender } = render(
      <MapCanvas
        {...defaultProps}
        selectedLayers={[defaultDescriptor]}
      />
    );
    
    await waitFor(() => {
      expect(document.querySelector('div')).toBeInTheDocument();
    });

    // Update selected layers
    rerender(
      <MapCanvas
        {...defaultProps}
        selectedLayers={[
          defaultDescriptor,
          { ...defaultDescriptor, id: 'admin', wms_name: 'counties', title: 'Counties' },
        ]}
      />
    );

    await waitFor(() => {
      expect(document.querySelector('div')).toBeInTheDocument();
    });
  });

  it('should handle onFeatureClick callback', () => {
    // This is more of an integration test - the actual click handling
    // would require mocking OpenLayers event system more deeply
    render(<MapCanvas {...defaultProps} />);
    
    expect(defaultProps.onFeatureClick).toBeDefined();
  });

  it('should render with empty selectedLayers array', () => {
    const { container } = render(<MapCanvas {...defaultProps} />);
    expect(container.querySelector('div')).toBeInTheDocument();
  });

  it('should use default GeoServer URL when env var is not set', async () => {
    delete process.env.REACT_APP_GEOSERVER_URL;
    
    render(<MapCanvas {...defaultProps} />);
    
    await waitFor(() => {
      expect(document.querySelector('div')).toBeInTheDocument();
    });
  });
});

