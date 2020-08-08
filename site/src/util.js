/* eslint-disable no-restricted-globals */
export function getMosaicFromQueryParams() {
  const params = new URLSearchParams(location.search);
  return params.get("mosaic");
}

export function setQueryParams(newParams = {}) {
  const params = new URLSearchParams(location.search);

  for (const [key, value] of Object.entries(newParams)) {
    params.set(String(key), String(value));
  }

  const newUrlString = `${location.pathname}?${params.toString()}${
    location.hash
  }`;
  window.history.replaceState({}, "", newUrlString);
}
/* eslint-enable no-restricted-globals */

/**
 * Get ViewState from page URL hash
 * Note: does not necessarily return all viewState fields
 * @param {string} hash Page URL hash
 */
export function getViewStateFromHash(hash) {
  if (!hash || hash.charAt(0) !== "#") {
    return;
  }

  // Split the hash into an array of numbers
  let hashArray = hash
    // Remove # symbol
    .substring(1)
    .split("/")
    .map(Number);

  // Remove non-numeric values
  hashArray = hashArray.map((val) => (Number.isFinite(val) && val) || null);

  // Order of arguments:
  // https://docs.mapbox.com/mapbox-gl-js/api/
  const [zoom, latitude, longitude, bearing, pitch] = hashArray;
  const viewState = {
    bearing,
    latitude,
    longitude,
    pitch,
    zoom,
  };

  // Delete null keys
  // https://stackoverflow.com/a/38340730
  Object.keys(viewState).forEach(
    (key) => viewState[key] == null && delete viewState[key]
  );

  return viewState;
}
