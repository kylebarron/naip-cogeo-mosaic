import React from "react";
import {
  Accordion,
  Checkbox,
  Card,
  Select,
  Icon,
  Container,
} from "semantic-ui-react";
import { mosaicOptions } from "./constants";

export default function InfoBox(props) {
  const { mosaicUrl, onChange } = props;

  return (
    <Container
      style={{
        position: "absolute",
        width: 280,
        maxWidth: 500,
        left: 10,
        top: 10,
        maxHeight: "70%",
        zIndex: 1,
        backgroundColor: "#fff",
        pointerEvents: "auto",
        overflowY: "auto",
        overflow: "visible",
      }}
    >
      <Select
        style={{ width: "100%" }}
        options={mosaicOptions}
        value={mosaicUrl}
        onChange={(e, data) => onChange(data.value)}
      />
    </Container>
  );
}
