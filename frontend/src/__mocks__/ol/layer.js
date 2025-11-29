function MockTileLayer(config) {
  this._properties = {};
  this._source = config ? config.source : null;

  this.set = jest.fn((key, value) => {
    this._properties[key] = value;
    return this;
  });
  this.setVisible = jest.fn((visible) => {
    this._properties.visible = visible;
    return this;
  });
  this.get = jest.fn((key) => {
    if (key === undefined) {
      return this._properties;
    }
    return this._properties[key];
  });
  this.getSource = jest.fn(() => {
    return this._source;
  });
  if (config) {
    if (config.visible !== undefined) {
      this._properties.visible = config.visible;
    }
  }
  return this;
}

module.exports = {
  Tile: MockTileLayer,
};

