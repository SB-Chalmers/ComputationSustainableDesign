function loadCSV(path, header, callback) {
    if (window.Worker) {
        const myWorker = new Worker("src/csvWorker.js");
        myWorker.onmessage = e => {
            callback(e.data);
            myWorker.terminate();
        };
        myWorker.postMessage([path, header]);
    } else {
        console.error("Workers not supported");
    }
}

export {loadCSV}