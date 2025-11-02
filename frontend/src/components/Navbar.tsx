// src/components/Navbar.tsx
import React from "react";

const Navbar: React.FC = () => {
  return (
    <nav className="bg-gray-800 text-white p-4 flex items-center shadow-lg">
      <h1 className="text-xl font-bold mr-auto">🇭🇷 Croatia Cadastral GIS</h1>
      <div className="flex space-x-4">
        <a href="/" className="hover:text-gray-300">Home</a>
        <a href="/about" className="hover:text-gray-300">About</a>
      </div>
    </nav>
  );
};

export default Navbar;

