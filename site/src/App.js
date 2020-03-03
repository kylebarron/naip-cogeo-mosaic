import React from "react";
import "./App.css";
import ReactMapGL, { Source, Layer } from "react-map-gl";

class App extends React.Component {
  state = {
      viewport: {
        latitude: 37.8,
        longitude: -122.4,
        zoom: 14,
        bearing: 0,
        pitch: 0
      }
    };

  landsatUrl = () => {
    const params = {
      bands: "4,3,2",
      color_ops: "gamma RGB 3.5, saturation 1.7, sigmoidal RGB 15 0.35"
    };
    const searchParams = new URLSearchParams(params);
    let baseUrl =
      "https://landsat-lambda.kylebarron.dev/tiles/e276a5acd25d7f2abc6c1233067628822d4de9c96b3c8977a168fee7/{z}/{x}/{y}@2x.png?";
    baseUrl += searchParams.toString();
    return baseUrl;

  }

  render() {
    return (
      <ReactMapGL
        {...this.state.viewport}
        width="100vw"
        height="100vh"
        mapOptions={{ hash: true }}
        mapStyle="https://raw.githubusercontent.com/kylebarron/fiord-color-gl-style/master/style.json"
        onViewportChange={viewport => this.setState({ viewport })}
      >
        <Source
          id="naip-lambda"
          type="raster"
          url="https://naip-lambda.kylebarron.dev/4c4d507790e8afa837215677bd6f74f58711bfaf3e1d5f7226193e12/tilejson.json?tile_scale=2"
          tileSize={512}
        >
          <Layer id="naip-lambda-layer" type="raster" />
        </Source>

        <Source
          id="landsat-lambda"
          type="raster"
          tileSize={512}
          tiles={[
            this.landsatUrl()
          ]}
          minzoom={7}
          maxzoom={12}
        >
          <Layer id="landsat-lambda-layer" type="raster" minzoom={7} maxzoom={12} />
        </Source>
      </ReactMapGL>
    );
  }
}

export default App;

document.body.style.margin = 0;
