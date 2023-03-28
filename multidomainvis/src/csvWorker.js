
importScripts("../libs/papaparse.min.js");

onmessage = function(e) {
    const [path, header] = e.data;
    Papa.parse(path, {
        download: true, dynamicTyping: true, header: header,
        complete: results => {
            postMessage(results.data);
        }
    });
}
