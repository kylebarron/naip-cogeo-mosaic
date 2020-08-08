import React from "react";
import "./App.css";
import ReactMapGL, {
  NavigationControl,
  ScaleControl,
  Layer,
} from "react-map-gl";
import { Map } from "immutable";
import InfoBox from "./info-box";
import {
  getViewStateFromHash,
  setQueryParams,
  getMosaicFromQueryParams,
} from "./util";
import { fullResMosaics, overviewMosaics } from "./constants";
const DEFAULT_MAP_STYLE = require("./style.json");

const INITIAL_MOSAIC_YEAR_RANGE = "2016-2018";
const INITIAL_VIEWPORT = {
  latitude: 36.07832,
  longitude: -111.8695,
  zoom: 13,
  bearing: 0,
  pitch: 0,
};

function naipUrl(mosaicUrl) {
  // Do saturation client side for speed
  // const color_ops = "sigmoidal RGB 4 0.5, saturation 1.25";
  const params = {
    url: mosaicUrl,
  };
  const searchParams = new URLSearchParams(params);
  let baseUrl = "https://us-west-2-lambda.kylebarron.dev/naip/{z}/{x}/{y}.jpg?";
  return baseUrl + searchParams.toString();
}

function constructMapStyle(mosaicYearRange) {
  const fullResMosaicUrl = fullResMosaics[mosaicYearRange];
  const overviewMosaicUrl = overviewMosaics[mosaicYearRange];

  DEFAULT_MAP_STYLE.sources["naip"] = {
    type: "raster",
    tiles: [naipUrl(fullResMosaicUrl)],
    tileSize: 256,
    minzoom: 12,
    maxzoom: 18,
    attribution:
      '<a href="https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/" target="_blank">© USDA</a>',
  };
  DEFAULT_MAP_STYLE.sources["naip-overview"] = {
    type: "raster",
    tiles: [naipUrl(overviewMosaicUrl)],
    tileSize: 256,
    minzoom: 6,
    maxzoom: 11,
    attribution:
      '<a href="https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/" target="_blank">© USDA</a>',
  };
  return Map(DEFAULT_MAP_STYLE);
}

class NAIPMap extends React.Component {
  render() {
    const { mapStyle, viewport, onViewportChange } = this.props;

    return (
      <ReactMapGL
        {...viewport}
        width="100vw"
        height="100vh"
        mapOptions={{ hash: true }}
        mapStyle={mapStyle}
        onViewportChange={onViewportChange}
        minZoom={4.5}
      >
        <Layer
          source="naip-overview"
          id="naip-layer-overview"
          type="raster"
          // No maxzoom to allow overzooming of imagery while higher-resolution
          // images load
          // Would be ideal to have all zooms at a single url root with a proxy
          // No maxzoom means zoom-12 tiles will load at higher zooms if panning
          // enough
          // maxzoom={12.5}
          beforeId="tunnel_motorway_link_casing"
          paint={{
            "raster-saturation": 0.35,
          }}
        />
        <Layer
          source="naip"
          id="naip-layer"
          type="raster"
          beforeId="tunnel_motorway_link_casing"
          paint={{
            "raster-saturation": 0.35,
          }}
        />

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
    viewport: {
      ...INITIAL_VIEWPORT,
      ...getViewStateFromHash(window.location.hash),
    },
    mosaicYearRange: getMosaicFromQueryParams() || INITIAL_MOSAIC_YEAR_RANGE,
    mapStyle: constructMapStyle(
      getMosaicFromQueryParams() || INITIAL_MOSAIC_YEAR_RANGE
    ),
  };

  render() {
    const { mosaicYearRange, mapStyle, viewport } = this.state;
    return (
      <div>
        <NAIPMap
          mapStyle={mapStyle}
          viewport={viewport}
          onViewportChange={(viewport) => this.setState({ viewport })}
        />
        <InfoBox
          mosaicYearRange={mosaicYearRange}
          zoomIn={viewport.zoom < 4.5}
          onChange={(selected) => {
            setQueryParams({ mosaic: selected });
            this.setState({
              mosaicYearRange: selected,
              mapStyle: constructMapStyle(selected),
            });
          }}
        />
      </div>
    );
  }
}

export default App;

document.body.style.margin = 0;
