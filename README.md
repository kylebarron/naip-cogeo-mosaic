[![Build Status](https://travis-ci.org/kylebarron/serverless-aerial-imagery.svg?branch=master)](https://travis-ci.org/kylebarron/serverless-aerial-imagery)

### Create mosaic

Install `cogeo-mosaic`, which takes `.tif` files as input and creates a
MosaicJSON. `cogeo-mosaic` depends on `pygeos`, which I've been unable to
install through pip, so I first install that through Conda.

```
conda install pygeos -c conda-forge -y
pip install cogeo-mosaic
```

Download manifest

```bash
aws s3 cp s3://naip-visualization/manifest.txt ./ --request-payer
```

```bash
cat manifest.txt \
    | awk -F '/' '{print $1}' \
    | uniq \
    | sed '/manifest.test/d' \
    > states.txt

cat states.txt | while read state
do
    cat manifest.txt \
        | grep "^${state}/" \
        | awk -F '/' '{print $2}' \
        | uniq \
        | sort -nr \
        | head -n 1 \
        | sed -e "s|^|${state}/|" \
        >> states_latest.txt
done

cat states_latest.txt | while read state_latest
do
    cat manifest.txt \
        | grep "^${state_latest}/" \
        | grep ".tif" \
        | sed -e 's|^|s3://naip-visualization/|' \
        >> tif_latest.txt
done
```

See how many tif images per state
```bash
cat states.txt | while read state
do
    # printf "State: $state "
    cat tif_latest.txt \
        | grep "^s3://naip-visualization/${state}/" \
        | wc -l
done
```

Example with Rhode Island
```bash
cat tif_latest.txt \
    | grep "^s3://naip-visualization/ri/" \
    | cogeo-mosaic footprint - > footprint.geojson
```

Total number of files
```bash
> wc -l tif_latest.txt
219068 tif_latest.txt
```

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

Just RI for now...
```bash
cat tif_latest.txt \
    | cogeo-mosaic create - --threads 2 \
    > naip_mosaic.json
```

### Deploy

```bash
git clone https://github.com/developmentseed/cogeo-mosaic-tiler.git

# Create lambda package
cd cogeo-mosaic-tiler & make package

# Deploy
npm install serverless -g
sls deploy --bucket kylebarron-landsat-test --region us-west-2
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
