import React from 'react';
import { render, screen } from '@testing-library/react';
import Navbar from './Navbar';

describe('Navbar', () => {
  it('should render the navbar with title', () => {
    render(<Navbar />);
    const title = screen.getByText(/Croatia Cadastral GIS/i);
    expect(title).toBeInTheDocument();
  });

  it('should render navigation links', () => {
    render(<Navbar />);
    const homeLink = screen.getByRole('link', { name: /home/i });
    const aboutLink = screen.getByRole('link', { name: /about/i });

    expect(homeLink).toBeInTheDocument();
    expect(aboutLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');
    expect(aboutLink).toHaveAttribute('href', '/about');
  });

  it('should have correct styling classes', () => {
    const { container } = render(<Navbar />);
    const nav = container.querySelector('nav');
    expect(nav).toHaveClass('bg-gray-800', 'text-white', 'p-4');
  });
});

