import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import DownloadMenu from "./DownloadMenu";
import { LayerDescriptor } from "../services/types";

describe("DownloadMenu", () => {
  const descriptor: LayerDescriptor = {
    id: "cadastral_parcels",
    title: "Cadastral Parcels",
    wms_name: "cadastral_parcels",
    workspace: "cro-geo-data",
  };

  const defaultProps = {
    activeLayer: descriptor,
    bbox: undefined as [number, number, number, number] | undefined,
  };

  beforeEach(() => {
    // Mock environment variable
    process.env.REACT_APP_GEOSERVER_URL = 'http://localhost:8080/geoserver';
  });

  afterEach(() => {
    delete process.env.REACT_APP_GEOSERVER_URL;
  });

  it("should render download menu with layer name", () => {
    render(<DownloadMenu {...defaultProps} />);
    
    expect(screen.getByText(/Download "Cadastral Parcels"/i)).toBeInTheDocument();
  });

  it("should render format dropdown with default GeoJSON selected", () => {
    render(<DownloadMenu {...defaultProps} />);
    
    const select = screen.getByRole('combobox');
    expect(select).toBeInTheDocument();
    expect(select).toHaveValue('application/json');
  });

  it("should render all format options", () => {
    render(<DownloadMenu {...defaultProps} />);
    
    const select = screen.getByRole('combobox');
    const options = Array.from(select.querySelectorAll('option'));
    
    expect(options.length).toBeGreaterThan(0);
    expect(screen.getByText('GeoJSON')).toBeInTheDocument();
    expect(screen.getByText('Shapefile (zip)')).toBeInTheDocument();
    expect(screen.getByText('KML')).toBeInTheDocument();
  });

  it("should update format when dropdown changes", async () => {
    const user = userEvent.setup();
    render(<DownloadMenu {...defaultProps} />);
    
    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'KML');
    
    expect(select).toHaveValue('KML');
  });

  it("should generate download link with correct WFS URL", () => {
    render(<DownloadMenu {...defaultProps} />);
    
    const downloadLink = screen.getByRole('link', { name: /download/i });
    const href = downloadLink.getAttribute('href');
    
    expect(href).toBeTruthy();
    expect(href).toContain('/wfs');
    expect(href).toContain('service=WFS');
    // URL is encoded, so check for encoded colon
    expect(href).toContain('typeName=cro-geo-data%3Acadastral_parcels');
    expect(href).toContain('outputFormat=application%2Fjson');
  });

  it("should include bbox in URL when provided", () => {
    const bbox: [number, number, number, number] = [100, 200, 300, 400];
    render(<DownloadMenu {...defaultProps} bbox={bbox} />);
    
    const downloadLink = screen.getByRole('link', { name: /download/i });
    const href = downloadLink.getAttribute('href');
    
    // URL is encoded
    expect(href).toContain('bbox=100%2C200%2C300%2C400%2CEPSG%3A3857');
  });

  it("should update download link when format changes", async () => {
    const user = userEvent.setup();
    render(<DownloadMenu {...defaultProps} />);
    
    const select = screen.getByRole('combobox');
    await user.selectOptions(select, 'shape-zip');
    
    const downloadLink = screen.getByRole('link', { name: /download/i });
    const href = downloadLink.getAttribute('href');
    
    // URL might be encoded depending on the format
    expect(href).toMatch(/outputFormat=(shape-zip|shape%2Dzip)/);
  });

  it("should open download link in new tab", () => {
    render(<DownloadMenu {...defaultProps} />);
    
    const downloadLink = screen.getByRole('link', { name: /download/i });
    
    expect(downloadLink).toHaveAttribute('target', '_blank');
    expect(downloadLink).toHaveAttribute('rel', 'noreferrer');
  });

  it("should use default GeoServer URL when env var is not set", () => {
    delete process.env.REACT_APP_GEOSERVER_URL;
    
    render(<DownloadMenu {...defaultProps} />);
    
    const downloadLink = screen.getByRole('link', { name: /download/i });
    const href = downloadLink.getAttribute('href');
    
    expect(href).toContain('http://localhost:8080/geoserver/wfs');
  });

  it("should handle different workspaces", () => {
    const customLayer: LayerDescriptor = {
      ...descriptor,
      workspace: "custom",
      wms_name: "boundaries",
      title: "Boundaries",
      id: "boundaries",
    };
    render(<DownloadMenu activeLayer={customLayer} bbox={undefined} />);

    const downloadLink = screen.getByRole("link", { name: /download/i });
    const href = downloadLink.getAttribute("href");

    expect(href).toContain("typeName=custom%3Aboundaries");
  });
});

