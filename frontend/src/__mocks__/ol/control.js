// Mock for ol/control
function MockScaleLine() {
  return this;
}

function mockDefaults() {
  return {
    extend: function(controls) {
      return controls || [];
    }
  };
}

module.exports = {
  defaults: mockDefaults,
  ScaleLine: MockScaleLine,
};

