import * as THREE from 'three';

import {Lut} from '../libs/Lut.js';
import {drawParticles, createColorbar} from './draw.js'

class DataHandler {
    constructor(scene) {
        this.scene = scene;
    }

    onBuildingOptionDataLoaded(geometry, cityOrigin, callback) {
        const origin = new THREE.Vector3(cityOrigin.x, 0, cityOrigin.y);
        geometry.rotateX(-Math.PI / 2);
        geometry.scale(1,1,-1);
        geometry.translate(-origin.x, -origin.y, -origin.z);
        geometry.scale(1,1,-1);
        const material = new THREE.MeshStandardMaterial({color: 0xAAAAAA, transparent: true, opacity: 0.8, flatShading: true});
        const mesh = new THREE.Mesh(geometry, material);
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        mesh.visible = false;
        this.scene.add(mesh);

        if (callback) {
            callback(mesh);
        }
    }

    onRadiationDataLoaded(data, dataSet, callback) {
        const positions = [];
        const colors = [];
        const lut = new Lut("blackbody", 32);

        const values = [];
        for (let d of data) {
            const value = d['value'];

            if (value === undefined) {
                console.log(d);
                continue;
            }

            positions.push(
                d["x"], // - 24.850166 , // Magic grid offset number
                51.3,
                - (d["y"]), // - 32.03199), // Magic grid offset number
            );

            values.push(value);
            lut.minV = Math.min(lut.minV, value);
            lut.maxV = Math.max(lut.maxV, value);
        }
        for (let v of values) {
            const color = lut.getColor(v);
            colors.push(color.r, color.g, color.b);
        }

        const mesh = drawParticles(positions, colors, 15, true);

        const title = dataSet.name === "Option 0" ? "Radiation, base case (kWh/m<sup>2</sup>)" : "Radiation, difference from base case (kWh/m<sup>2</sup>)"
        const colorbar = createColorbar(lut, title);
        document.getElementById("legendContainer").append(colorbar);

        this.scene.add(mesh);
        mesh.visible = false;


        if (callback) {
            callback(mesh, colorbar);
        }
    }

    onWindDataLoaded(cellData, nodeData, cityOrigin, callback) {
        const worker = new Worker("src/windDataWorker.js");
        worker.onmessage = e => {
            const geometry = new THREE.BufferGeometry();
            const colors = [];
            for (let hex of e.data.colors) {
                const color = new THREE.Color(hex);
                colors.push(color.r, color.g, color.b);
            }
            geometry.setIndex(e.data.indices);
            geometry.setAttribute('position', new THREE.Float32BufferAttribute(e.data.positions, 3));
            geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
            geometry.setAttribute('normal', new THREE.Float32BufferAttribute(e.data.normals, 3));
            const material = new THREE.MeshStandardMaterial({
                color: 0xF5F5F5,
                vertexColors: true
            });
            const mesh = new THREE.Mesh(geometry, material);

            mesh.castShadow = true;
            mesh.receiveShadow = true;

            const colorbar = document.createElement('img');
            colorbar.classList.add('legend');
            colorbar.style.padding = '5px';
            colorbar.src = "data/wind/surfaceLawson_option_0.png";
            document.getElementById("legendContainer").append(colorbar);

            mesh.visible = false;
            this.scene.add(mesh);

            if (callback) {
                callback(mesh, colorbar);
            }
        }
        worker.postMessage([cellData, nodeData, cityOrigin]);
    }

    onNoiseDataLoaded(data, cityOrigin, callback) {
        const positions = [];
        const colors = [];
        const lut = new Lut("rainbow", 32);

        const noiseVals = [];
        for (let d of data) {
            let [x, y, noiseVal] = d;
            if (isNaN(noiseVal)) {
                continue;
            }
            positions.push(
                x - cityOrigin.x,
                59.7,
                - (y - cityOrigin.y)
            );
            noiseVals.push(noiseVal);
        }
        lut.minV = Math.min(...noiseVals);
        lut.maxV = Math.max(...noiseVals);

        for (let v of noiseVals) {
            const color = lut.getColor(v);
            colors.push(color.r, color.g, color.b);
        }

        const mesh = drawParticles(positions, colors, 4);
        mesh.visible = false;
        this.scene.add(mesh);

        const colorbar = createColorbar(lut, "Noise (dB)");
        document.getElementById("legendContainer").append(colorbar);

        if (callback) {
            callback(mesh, colorbar);
        }
    }

    onCityDataLoaded(loadedData, energyMap, callback) {
        const lut = new Lut('rainbow', 32);
        for (let building of energyMap.values()) {
            lut.minV = Math.min(lut.minV, building.Total);
            lut.maxV = Math.max(lut.maxV, building.Total);
        }

        const buildings = loadedData.Buildings;

        const buildingGroup = new THREE.Group();

        for (let building of buildings) {
            const points = building.Footprint.map(p => new THREE.Vector2(p.x, p.y));
            const shape = new THREE.Shape(points);
            const geometry = new THREE.ExtrudeGeometry(shape, {
                steps: 1,
                depth: building.Height,
                bevelEnabled: false
            });

            let color = 0xffffff;
            if (energyMap.has(building.UUID)) {
                color = lut.getColor(energyMap.get(building.UUID).Total)
            }
            const material = new THREE.MeshStandardMaterial({color});
            const mesh = new THREE.Mesh(geometry, material);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            mesh.position.z = building.GroundHeight;
            buildingGroup.add(mesh);
        }
        buildingGroup.rotateX(-Math.PI / 2);
        buildingGroup.visible = false;
        this.scene.add(buildingGroup);

        let colorbar
        if (energyMap.size > 0) {
            colorbar = createColorbar(lut, "Energy (kWh/m<sup>2</sup>)");
            document.getElementById("legendContainer").append(colorbar);
        }

        if(callback) {
            callback(buildingGroup, colorbar);
        }

        return loadedData.Origin;
    }

}

export {DataHandler}