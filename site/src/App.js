import React from "react";
import "./App.css";
import ReactMapGL, { Source, Layer } from "react-map-gl";

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      viewport: {
        latitude: 37.8,
        longitude: -122.4,
        zoom: 14,
        bearing: 0,
        pitch: 0
      }
    };
  }

  render() {
    return (
      <ReactMapGL
        {...this.state.viewport}
        width="100vw"
        height="100vh"
        mapStyle="https://raw.githubusercontent.com/kylebarron/fiord-color-gl-style/master/style.json"
        onViewportChange={viewport => this.setState({ viewport })}
      >
        <Source
          id="naip"
          type="raster"
          url="https://naip-lambda.kylebarron.dev/4c4d507790e8afa837215677bd6f74f58711bfaf3e1d5f7226193e12/tilejson.json?tile_scale=2"
          tileSize={512}
        >
          <Layer id="naip-layer" type="raster" />
        </Source>
      </ReactMapGL>
    );
  }
}

export default App;

document.body.style.margin = 0;
