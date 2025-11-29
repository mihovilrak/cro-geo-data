import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MetadataPopup from './MetadataPopup';

const mockProperties = {
  ogc_fid: 1,
  parcel_id: '12345',
  cadastral_municipality: 'Zagreb',
  area_sqm: 5000,
  updated_at: '2024-01-15',
};

describe('MetadataPopup', () => {
  const defaultProps = {
    properties: mockProperties,
    onClose: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render nothing when properties is null', () => {
    const { container } = render(
      <MetadataPopup properties={null} onClose={jest.fn()} />
    );

    expect(container.firstChild).toBeNull();
  });

  it('should render metadata popup with title', () => {
    render(<MetadataPopup {...defaultProps} />);

    expect(screen.getByText(/Feature Metadata/i)).toBeInTheDocument();
  });

  it('should render all property key-value pairs', () => {
    render(<MetadataPopup {...defaultProps} />);

    expect(screen.getByText(/ogc_fid:/i)).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText(/parcel_id:/i)).toBeInTheDocument();
    expect(screen.getByText('12345')).toBeInTheDocument();
    expect(screen.getByText(/cadastral_municipality:/i)).toBeInTheDocument();
    expect(screen.getByText('Zagreb')).toBeInTheDocument();
    expect(screen.getByText(/area_sqm:/i)).toBeInTheDocument();
    expect(screen.getByText('5000')).toBeInTheDocument();
  });

  it('should convert all values to strings', () => {
    render(<MetadataPopup {...defaultProps} />);

    const value = screen.getByText('5000');
    expect(value).toBeInTheDocument();
  });

  it('should call onClose when close button is clicked', async () => {
    const user = userEvent.setup();
    const onClose = jest.fn();

    render(<MetadataPopup {...defaultProps} onClose={onClose} />);

    const closeButton = screen.getByRole('button', { name: /close/i });
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('should handle empty properties object', () => {
    render(
      <MetadataPopup
        properties={{}}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText(/Feature Metadata/i)).toBeInTheDocument();
    expect(screen.queryByText(/:/)).not.toBeInTheDocument();
  });

  it('should render with complex property values', () => {
    const complexProperties = {
      name: 'Test',
      coordinates: [100, 200],
      nested: { key: 'value' },
    };

    render(
      <MetadataPopup
        properties={complexProperties}
        onClose={jest.fn()}
      />
    );

    expect(screen.getByText(/name:/i)).toBeInTheDocument();
    expect(screen.getByText('Test')).toBeInTheDocument();
  });
});

