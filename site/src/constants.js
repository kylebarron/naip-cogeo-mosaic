// Mapping from mosaic common identifier to URL
export const fullResMosaics = {
  "2011-2013":
    "dynamodb://us-west-2/74f48044f38db32666078e75f3439d8e62cf9e25820afc79ea6ce19f",
  "2014-2015":
    "dynamodb://us-west-2/5395d9e7bba4eeaa6af4842e1a7b9d3ea9dfc2a74373ae24698809e9",
  "2015-2017":
    "dynamodb://us-west-2/7610d6d77fca346802fb21b89668cb12ef3162a31eb71734a8aaf5de",
  "2016-2018":
    "dynamodb://us-west-2/94c61bd217e1211db47cf7f8b95bbc8e5e7d68a26cd9099319cf15f9",
};

// Mapping from mosaic common identifier to URL
export const overviewMosaics = {
  "2011-2013":
    "s3://mosaics-us-west-2.kylebarron.dev/mosaics/naip/naip_overview_2011_2013.json.gz",
  "2014-2015":
    "s3://mosaics-us-west-2.kylebarron.dev/mosaics/naip/naip_overview_2014_2015.json.gz",
  "2015-2017":
    "s3://mosaics-us-west-2.kylebarron.dev/mosaics/naip/naip_overview_2015_2017.json.gz",
  "2016-2018":
    "s3://mosaics-us-west-2.kylebarron.dev/mosaics/naip/naip_overview_2016_2018.json.gz",
};

export const mosaicOptions = [
  {
    key: "2011-2013",
    value: "2011-2013",
    text: "Imagery Range: 2011-2013",
  },
  {
    key: "2014-2015",
    value: "2014-2015",
    text: "Imagery Range: 2014-2015",
  },
  {
    key: "2015-2017",
    value: "2015-2017",
    text: "Imagery Range: 2015-2017",
  },
  {
    key: "2016-2018",
    value: "2016-2018",
    text: "Imagery Range: 2016-2018",
  },
];
