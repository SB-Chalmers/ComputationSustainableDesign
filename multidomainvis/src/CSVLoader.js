class CSVLoader {

    constructor(nWorkers) {
        this.queue = [];
        this.availableWorkers = [];
        for (let i=0; i<nWorkers; i++) {
            if (window.Worker) {
                this.availableWorkers.push(new Worker("src/csvWorker.js"));
            } else {
                console.error("Workers not supported");
            }
        }
    }

    loadCSV(path, header, callback) {
        this.queue.push({
            path: path,
            header: header,
            callback: callback
        });
        this.processQueue();
    }

    processQueue() {
        while (
            this.availableWorkers.length > 0 &&
            this.queue.length > 0
        ) {
            let worker = this.availableWorkers.pop();
            let job = this.queue.splice(0, 1)[0];
            worker.onmessage = e => {
                job.callback(e.data);
                this.availableWorkers.push(worker);
                this.processQueue();
            };
            worker.postMessage([job.path, job.header]);
        }
    }

    decommission() {
        this.availableWorkers.forEach(w=>w.terminate());
    }
}

export {CSVLoader}