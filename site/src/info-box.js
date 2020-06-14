import React from "react";
import { Header, Select, Icon, Container } from "semantic-ui-react";
import { mosaicOptions } from "./constants";

export default function InfoBox(props) {
  const { mosaicUrl, onChange, zoomIn } = props;

  return (
    <Container
      style={{
        position: "absolute",
        width: 280,
        maxWidth: 500,
        left: 10,
        top: 10,
        padding: 5,
        maxHeight: "70%",
        zIndex: 1,
        backgroundColor: "#fff",
        pointerEvents: "auto",
        overflowY: "auto",
        overflow: "visible",
      }}
    >
      <Header as="h3">Serverless Tiled NAIP Imagery</Header>
      <p>
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://github.com/kylebarron/naip-cogeo-mosaic"
        >
          <Icon name="github" />
          Github
        </a>
      </p>
      <p>
        Serverless high-resolution NAIP map tiles, generated on demand from an{" "}
        <a
          target="_blank"
          rel="noopener noreferrer"
          href="https://registry.opendata.aws/naip/"
        >
          AWS public dataset
        </a>{" "}
        of Cloud-Optimized GeoTIFFs.
      </p>

      {zoomIn && <p> Zoom in to see imagery.</p>}
      <Select
        style={{ width: "100%" }}
        options={mosaicOptions}
        value={mosaicUrl}
        onChange={(e, data) => onChange(data.value)}
      />
    </Container>
  );
}
