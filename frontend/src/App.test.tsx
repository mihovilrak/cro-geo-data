import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import { LayerDescriptor } from './services/types';

const mockCatalog: LayerDescriptor[] = [
  { id: 'cadastral_parcels', title: 'Cadastral Parcels', wms_name: 'cadastral_parcels', workspace: 'cro-geo-data', default: true },
  { id: 'counties', title: 'Administrative Boundaries', wms_name: 'counties', workspace: 'cro-geo-data', default: false },
];

jest.mock('./services/apiClient', () => ({
  fetchLayerCatalog: jest.fn().mockResolvedValue(mockCatalog),
}));

jest.mock('./components/MapCanvas', () => {
  return function MockMapCanvas({ selectedLayers, activeBaseLayer }: any) {
    return (
      <div data-testid="map-canvas">
        <div>Map Canvas</div>
        <div>
          Selected Layers: {selectedLayers.map((layer: LayerDescriptor) => layer.id).join(', ')}
        </div>
        <div>Base Layer: {activeBaseLayer}</div>
      </div>
    );
  };
});

describe('App', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render navbar', () => {
    render(<App />);
    expect(screen.getByText(/Croatia Cadastral GIS/i)).toBeInTheDocument();
  });

  it('should render layer switcher', () => {
    render(<App />);
    expect(screen.getByText(/Background Layer/i)).toBeInTheDocument();
    expect(screen.getByText(/Data Layers/i)).toBeInTheDocument();
  });

  it('should render map canvas', () => {
    render(<App />);
    expect(screen.getByTestId('map-canvas')).toBeInTheDocument();
  });

  it('should initialize with available layers', async () => {
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Cadastral Parcels/i)).toBeInTheDocument();
      expect(screen.getByText(/Administrative Boundaries/i)).toBeInTheDocument();
    });
  });

  it('should initialize with OSM as default base layer', () => {
    render(<App />);
    const osmRadio = screen.getByLabelText(/OpenStreetMap/i);
    expect(osmRadio).toBeChecked();
  });

  it('should toggle base layer when radio button is clicked', async () => {
    const user = userEvent.setup();
    render(<App />);
    const dofRadio = screen.getByLabelText(/DOF/i);
    await user.click(dofRadio);
    expect(dofRadio).toBeChecked();
    await waitFor(() => {
      expect(screen.getByText(/Base Layer: DOF/i)).toBeInTheDocument();
    });
  });

  it('should toggle layer selection when checkbox is clicked', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Cadastral Parcels/i)).toBeInTheDocument();
    });
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    await user.click(layer1Checkbox);
    expect(layer1Checkbox).toBeChecked();
    await waitFor(() => {
      const mapText = screen.getByText(/Selected Layers:/i);
      expect(mapText).toHaveTextContent(/cadastral_parcels/i);
    });
  });

  it('should deselect layer when clicked again', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Cadastral Parcels/i)).toBeInTheDocument();
    });
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    await user.click(layer1Checkbox);
    expect(layer1Checkbox).toBeChecked();
    await user.click(layer1Checkbox);
    expect(layer1Checkbox).not.toBeChecked();
  });

  it('should not show metadata popup initially', () => {
    render(<App />);
    expect(screen.queryByText(/Feature Metadata/i)).not.toBeInTheDocument();
  });

  it('should not show download menu when no layer is selected', () => {
    render(<App />);
    expect(screen.queryByText(/Download/i)).not.toBeInTheDocument();
  });

  it('should show download menu when a layer is selected', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Cadastral Parcels/i)).toBeInTheDocument();
    });
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    await user.click(layer1Checkbox);
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /download/i })).toBeInTheDocument();
    });
  });

  it('should handle multiple layer selection', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Cadastral Parcels/i)).toBeInTheDocument();
    });
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    const layer2Checkbox = screen.getByRole('checkbox', {
      name: /administrative boundaries/i,
    });
    await user.click(layer1Checkbox);
    await user.click(layer2Checkbox);
    expect(layer1Checkbox).toBeChecked();
    expect(layer2Checkbox).toBeChecked();
    await waitFor(() => {
      const mapText = screen.getByText(/Selected Layers:/i);
      expect(mapText).toHaveTextContent(/cadastral_parcels/i);
      expect(mapText).toHaveTextContent(/counties/i);
    });
  });

  it('should update current layer when layer is toggled', async () => {
    const user = userEvent.setup();
    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/Cadastral Parcels/i)).toBeInTheDocument();
    });
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    await user.click(layer1Checkbox);
    await waitFor(() => {
      expect(screen.getByText(/Download "Cadastral Parcels"/i)).toBeInTheDocument();
    });
  });
});

