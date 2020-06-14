import React from "react";
import "./App.css";
import ReactMapGL, { Source, Layer } from "react-map-gl";
import Seo from "./seo";

class Map extends React.Component {
  state = {
    viewport: {
      latitude: 36.07832,
      longitude: -111.8695,
      zoom: 13,
      bearing: 0,
      pitch: 0,
    },
  };

  naipUrl = () => {
    const color_ops = "sigmoidal RGB 4 0.5, saturation 1.25";
    // 2016-2018 mosaic
    const mosaicUrl =
      "dynamodb://us-west-2/94c61bd217e1211db47cf7f8b95bbc8e5e7d68a26cd9099319cf15f9";

    const params = {
      url: mosaicUrl,
      color_ops,
    };
    const searchParams = new URLSearchParams(params);
    let baseUrl =
      "https://us-west-2-lambda.kylebarron.dev/naip/{z}/{x}/{y}@2x.jpg?";
    return baseUrl + searchParams.toString();
  };

  render() {
    return (
      <ReactMapGL
        {...this.state.viewport}
        width="100vw"
        height="100vh"
        mapOptions={{ hash: true }}
        mapStyle="https://raw.githubusercontent.com/kylebarron/fiord-color-gl-style/master/style.json"
        onViewportChange={(viewport) => this.setState({ viewport })}
      >
        <Source
          id="naip-lambda"
          type="raster"
          tiles={[this.naipUrl()]}
          tileSize={512}
          minzoom={12}
          maxzoom={17}
          attribution='<a href="https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/" target="_blank">© USDA</a>'
        >
          <Layer id="naip-lambda-layer" type="raster" />
        </Source>
      </ReactMapGL>
    );
  }
}

function App(props) {
  return (
    <div>
      <Seo
        siteUrl="https://kylebarron.dev/naip-cogeo-mosaic"
        title="naip-cogeo-mosaic"
        description="Serverless high-resolution NAIP map tiles from Cloud-Optimized GeoTIFFs for the lower 48 U.S. states."
        imageUrl="/share_preview_grca.jpg"
        twitterProfile="@kylebarron"
      />
      <Map />
    </div>
  );
}

export default App;

document.body.style.margin = 0;
