
importScripts("../libs/papaparse.min.js");

onmessage = function(e) {
    const [path, header] = e.data;
    Papa.parse(path, {
        download: true, dynamicTyping: true, header: header, skipEmptyLines: true,
        complete: results => {
            postMessage(results.data);
        }
    });
}
