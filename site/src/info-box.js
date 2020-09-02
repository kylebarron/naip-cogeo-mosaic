import React from "react";
import { Accordion, Select, Icon } from "semantic-ui-react";
import { mosaicOptions } from "./constants";

export default function InfoBox(props) {
  const { mosaicYearRange, onChange, zoomIn } = props;

  const panels = [
    {
      key: "header",
      title: "Serverless High-Resolution Imagery",
      content: {
        content: (
          <p>
            Serverless high-resolution (up to 0.6m){" "}
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://www.fsa.usda.gov/programs-and-services/aerial-photography/imagery-programs/naip-imagery/"
            >
              NAIP
            </a>{" "}
            map tiles, generated on demand from an{" "}
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://registry.opendata.aws/naip/"
            >
              AWS public dataset
            </a>{" "}
            of Cloud-Optimized GeoTIFFs.
            <br />
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://github.com/kylebarron/naip-cogeo-mosaic"
            >
              <Icon name="github" />
              Github
            </a>
            <br />
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://kylebarron.dev/blog/cog-mosaic/naip"
            >
              <Icon name="book" />
              Blog post
            </a>
          </p>
        ),
      },
    },
  ];

  return (
    <div
      style={{
        position: "absolute",
        width: 300,
        maxWidth: 400,
        left: 5,
        top: 5,
        padding: 5,
        maxHeight: "70%",
        zIndex: 1,
        // backgroundColor: "#fff",
        pointerEvents: "auto",
        overflowY: "auto",
        overflow: "visible",
      }}
    >
      <Accordion defaultActiveIndex={0} styled panels={panels} />
      {/* <Header as="h3">Serverless High-Res Imagery</Header> */}

      {zoomIn && (
        <p>
          <b> Zoom in to see imagery. </b>
        </p>
      )}
      <Select
        style={{ width: "100%" }}
        options={mosaicOptions}
        value={mosaicYearRange}
        onChange={(e, data) => onChange(data.value)}
      />
    </div>
  );
}
