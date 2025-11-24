function MockOSM() {
  return this;
}

function MockTileWMS(config) {
  this.getFeatureInfoUrl = jest.fn(() => 'http://mock-url.com');
  return this;
}

module.exports = {
  OSM: MockOSM,
  TileWMS: MockTileWMS,
};

