import React from "react";
import "./App.css";
import ReactMapGL, {
  NavigationControl,
  ScaleControl,
  Layer,
} from "react-map-gl";
import { Map } from "immutable";

const defaultMapStyle = require("./style.json");
const mosaicUrls = {
  "2011-2013":
    "dynamodb://us-west-2/74f48044f38db32666078e75f3439d8e62cf9e25820afc79ea6ce19f",
  "2014-2015":
    "dynamodb://us-west-2/5395d9e7bba4eeaa6af4842e1a7b9d3ea9dfc2a74373ae24698809e9",
  "2015-2017":
    "dynamodb://us-west-2/7610d6d77fca346802fb21b89668cb12ef3162a31eb71734a8aaf5de",
  "2016-2018":
    "dynamodb://us-west-2/94c61bd217e1211db47cf7f8b95bbc8e5e7d68a26cd9099319cf15f9",
};
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

function constructMapStyle(mosaic_choice) {
  defaultMapStyle.sources["naip"] = {
    type: "raster",
    tiles: [naipUrl(mosaicUrls[mosaic_choice])],
    tileSize: 512,
    minzoom: 12,
    maxzoom: 17,
    attribution:
      '<a href="https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/" target="_blank">© USDA</a>',
  };
  return Map(defaultMapStyle);
}

class NAIPMap extends React.Component {
  state = {
    viewport: {
      latitude: 36.07832,
      longitude: -111.8695,
      zoom: 13,
      bearing: 0,
      pitch: 0,
    },
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
    mosaicChoice: "2016-2018",
    mapStyle: constructMapStyle("2016-2018"),
  };

  render() {
    const { mosaicChoice } = this.state;
    return (
      <div>
        <NAIPMap mosaicChoice={mosaicChoice} />
        <InfoBox
          mosaicChoice={mosaicChoice}
          onChange={(selected) =>
            this.setState({
              mosaicChoice: selected,
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
