// Mock for ol main module
function MockMap(config) {
  this._layers = [];
  this.getView = jest.fn(() => ({
    getResolution: jest.fn(() => 1000),
  }));
  this.getLayers = jest.fn(() => ({
    getArray: jest.fn(() => this._layers),
  }));
  this.on = jest.fn();
  this.addLayer = jest.fn((layer) => {
    this._layers.push(layer);
  });
  this.removeLayer = jest.fn((layer) => {
    const index = this._layers.indexOf(layer);
    if (index > -1) {
      this._layers.splice(index, 1);
    }
  });
  // Store layers from config if provided
  if (config && config.layers) {
    this._layers = config.layers.slice();
  }
  return this;
}

function MockView(config) {
  this.getResolution = jest.fn(() => 1000);
  return this;
}

module.exports = {
  Map: MockMap,
  View: MockView,
};

