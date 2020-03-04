[![Build Status](https://travis-ci.org/kylebarron/serverless-aerial-imagery.svg?branch=master)](https://travis-ci.org/kylebarron/serverless-aerial-imagery)

## Install

```
git clone --recurse-submodules https://github.com/kylebarron/naip-lambda
cd naip-lambda
conda env create -f environment.yml
source activate naip-lambda
```

### Select TIF URLs

Download manifest

```bash
aws s3 cp s3://naip-visualization/manifest.txt ./ --request-payer
```

Select URLs by years

```bash
python code/naip.py manifest \
    -s 2011 \
    -e 2013 \
    manifest.txt \
    | sed -e 's|^|s3://naip-visualization/|' \
    > urls_2011_2013.txt
python code/naip.py manifest \
    -s 2014 \
    -e 2015 \
    manifest.txt \
    | sed -e 's|^|s3://naip-visualization/|' \
    > urls_2014_2015.txt
python code/naip.py manifest \
    -s 2015 \
    -e 2017 \
    manifest.txt \
    | sed -e 's|^|s3://naip-visualization/|' \
    > urls_2015_2017.txt
```

As an example, you can get the mosaic footprint of Rhode Island
```bash
cat urls_2011_2013.txt \
    | grep "^s3://naip-visualization/ri/" \
    | cogeo-mosaic footprint - > footprint.geojson
```

And inspect it with [kepler.gl](https://github.com/kylebarron/keplergl_cli):
```bash
kepler footprint.geojson
```

![](assets/rhode_island_footprint.png)

Here you can see that the tiles to be used in the mosaic of Rhode Island don't
include the state's border. That's because the Python script to parse the
manifest deduplicates tiles on the border when they're include in both states.
If you looked at the footprint of Connecticut, you'd see the missing tiles on
the border.

Total number of files
```bash
> wc -l urls_2011_2013.txt
  213197 urls_2011_2013.txt
```

### Create MosaicJSON

NAIP imagery tiffs are in a requester pays bucket. In order to access them, you
need to set the `AWS_REQUEST_PAYER` environment variable:

```bash
export AWS_REQUEST_PAYER="requester"
```

I also found that on an AWS EC2 instance; `cogeo-mosaic create` was failing
while it was working on my local computer. In general, if `cogeo-mosaic create`
isn't working for some URL; you should run `rio info <URL>` and see what the
error is, since `cogeo-mosaic` uses `rasterio` internally, but doesn't currently
print `rasterio` errors to stdout. In my case, I had to set the certificates
path (see
[cogeotiff/rio-tiler#19](https://github.com/cogeotiff/rio-tiler/issues/19),
[mapbox/rasterio#942](https://github.com/mapbox/rasterio/issues/942)).

```bash
export CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
```

Then create the MosaicJSON file. GET requests are priced at `$0.0004` per 1000
requests, so creating the MosaicJSON should cost `0.0004 * (219068 / 1000) =
0.087`. 9 cents!

```bash
cat urls_2011_2013.txt \
    | cogeo-mosaic create - \
    > naip_2011_2013_mosaic.json
```

### Deploy

```bash
# Create lambda package
cd cogeo-mosaic-tiler & make package

# Deploy
npm install serverless -g
sls deploy --bucket bucket-name --region us-west-2
```

Add the mosaic json

```bash
export ENDPOINT_URL="..."
export ENDPOINT_URL="https://e2pot5hhjk.execute-api.us-west-2.amazonaws.com/production"
curl -X POST -d @list.json "${ENDPOINT_URL}/add"
```

### Custom endpoint

```
https://us-west-2.console.aws.amazon.com/acm/home?region=us-west-2#/firstrun/
```

Go to Cloudflare > Choose Domain > SSL/TLS > Origin Server > Create Certificate.

https://support.cloudflare.com/hc/en-us/articles/115000479507#h_30cc332c-8f6e-42d8-9c59-6c1f06650639
