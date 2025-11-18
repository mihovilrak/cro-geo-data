import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LayerSwitcher from "./LayerSwitcher";
import { LayerDescriptor } from "../services/types";

const mockAvailableLayers: LayerDescriptor[] = [
  { id: "layer1", title: "Cadastral Parcels", wms_name: "cadastral_parcels" },
  { id: "layer2", title: "Administrative Boundaries", wms_name: "counties" },
];

const defaultProps = {
  availableLayers: mockAvailableLayers,
  selectedLayers: [],
  toggleLayer: jest.fn(),
  toggleBase: jest.fn(),
  activeBase: "OSM" as const,
  isLoading: false,
  error: undefined,
};

describe('LayerSwitcher', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render background layer options', () => {
    render(<LayerSwitcher {...defaultProps} />);
    
    expect(screen.getByText(/Background Layer/i)).toBeInTheDocument();
    expect(screen.getByText(/OpenStreetMap/i)).toBeInTheDocument();
    expect(screen.getByText(/DOF/i)).toBeInTheDocument();
  });

  it('should render data layers section', () => {
    render(<LayerSwitcher {...defaultProps} />);
    
    expect(screen.getByText(/Data Layers/i)).toBeInTheDocument();
    expect(screen.getByText('Cadastral Parcels')).toBeInTheDocument();
    expect(screen.getByText('Administrative Boundaries')).toBeInTheDocument();
  });

  it('should display OSM as checked when activeBase is OSM', () => {
    render(<LayerSwitcher {...defaultProps} activeBase="OSM" />);
    
    const osmRadio = screen.getByLabelText(/OpenStreetMap/i);
    const dofRadio = screen.getByLabelText(/DOF/i);
    
    expect(osmRadio).toBeChecked();
    expect(dofRadio).not.toBeChecked();
  });

  it('should display DOF as checked when activeBase is DOF', () => {
    render(<LayerSwitcher {...defaultProps} activeBase="DOF" />);
    
    const osmRadio = screen.getByLabelText(/OpenStreetMap/i);
    const dofRadio = screen.getByLabelText(/DOF/i);
    
    expect(osmRadio).not.toBeChecked();
    expect(dofRadio).toBeChecked();
  });

  it('should call toggleBase when base layer radio is clicked', async () => {
    const user = userEvent.setup();
    const toggleBase = jest.fn();
    
    render(<LayerSwitcher {...defaultProps} toggleBase={toggleBase} />);
    
    const dofRadio = screen.getByLabelText(/DOF/i);
    await user.click(dofRadio);
    
    expect(toggleBase).toHaveBeenCalledWith('DOF');
  });

  it('should check selected layers', () => {
    render(
      <LayerSwitcher
        {...defaultProps}
        selectedLayers={["layer1"]}
      />
    );
    
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    const layer2Checkbox = screen.getByRole('checkbox', {
      name: /administrative boundaries/i,
    });
    
    expect(layer1Checkbox).toBeChecked();
    expect(layer2Checkbox).not.toBeChecked();
  });

  it('should call toggleLayer when layer checkbox is clicked', async () => {
    const user = userEvent.setup();
    const toggleLayer = jest.fn();
    
    render(
      <LayerSwitcher
        {...defaultProps}
        toggleLayer={toggleLayer}
      />
    );
    
    const layer1Checkbox = screen.getByRole('checkbox', {
      name: /cadastral parcels/i,
    });
    await user.click(layer1Checkbox);

    expect(toggleLayer).toHaveBeenCalledWith("layer1");
  });

  it('should display "No layers available" when availableLayers is empty', () => {
    render(
      <LayerSwitcher
        {...defaultProps}
        availableLayers={[]}
        isLoading={false}
      />
    );
    
    expect(screen.getByText(/No layers available/i)).toBeInTheDocument();
  });

  it('should render loading state', () => {
    render(
      <LayerSwitcher
        {...defaultProps}
        isLoading
        availableLayers={[]}
      />
    );

    expect(screen.getByText(/Loading layers/i)).toBeInTheDocument();
  });

  it('should render error state', () => {
    render(
      <LayerSwitcher
        {...defaultProps}
        availableLayers={[]}
        error="boom"
      />
    );

    expect(screen.getByText(/boom/i)).toBeInTheDocument();
  });
});

