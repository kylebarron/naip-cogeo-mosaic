import React from "react";
import "./App.css";
import ReactMapGL, {
  NavigationControl,
  ScaleControl,
  Layer,
} from "react-map-gl";
import { Map } from "immutable";
import InfoBox from "./info-box";

const INITIAL_MOSAIC_URL =
  "dynamodb://us-west-2/94c61bd217e1211db47cf7f8b95bbc8e5e7d68a26cd9099319cf15f9";
const INITIAL_VIEWPORT = {
  latitude: 36.07832,
  longitude: -111.8695,
  zoom: 13,
  bearing: 0,
  pitch: 0,
};
const DEFAULT_MAP_STYLE = require("./style.json");

function naipUrl(mosaicUrl) {
  const color_ops = "sigmoidal RGB 4 0.5, saturation 1.25";
  const params = {
    url: mosaicUrl,
    color_ops,
  };
  const searchParams = new URLSearchParams(params);
  let baseUrl =
    "https://us-west-2-lambda.kylebarron.dev/naip/{z}/{x}/{y}@2x.jpg?";
  return baseUrl + searchParams.toString();
}

function constructMapStyle(mosaicUrl) {
  DEFAULT_MAP_STYLE.sources["naip"] = {
    type: "raster",
    tiles: [naipUrl(mosaicUrl)],
    tileSize: 512,
    minzoom: 12,
    maxzoom: 17,
    attribution:
      '<a href="https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/" target="_blank">© USDA</a>',
  };
  return Map(DEFAULT_MAP_STYLE);
}

class NAIPMap extends React.Component {
  state = {
    viewport: INITIAL_VIEWPORT,
  };

  render() {
    const { viewport } = this.state;
    const { mapStyle } = this.props;

    return (
      <ReactMapGL
        {...viewport}
        width="100vw"
        height="100vh"
        mapOptions={{ hash: true }}
        mapStyle={mapStyle}
        onViewportChange={(viewport) => this.setState({ viewport })}
      >
        <Layer source="naip" id="naip-layer" type="raster" />

        <div style={{ position: "absolute", right: 10, top: 10 }}>
          <NavigationControl />
        </div>

        <div style={{ position: "absolute", bottom: 10, left: 10 }}>
          <ScaleControl maxWidth={100} unit={"imperial"} />
        </div>
      </ReactMapGL>
    );
  }
}

class App extends React.Component {
  state = {
    mosaicUrl: INITIAL_MOSAIC_URL,
    mapStyle: constructMapStyle(INITIAL_MOSAIC_URL),
  };

  render() {
    const { mosaicUrl, mapStyle } = this.state;
    return (
      <div>
        <NAIPMap mapStyle={mapStyle} />
        <InfoBox
          mosaicUrl={mosaicUrl}
          onChange={(selected) =>
            this.setState({
              mosaicUrl: selected,
              mapStyle: constructMapStyle(selected),
            })
          }
        />
      </div>
    );
  }
}

export default App;

document.body.style.margin = 0;
