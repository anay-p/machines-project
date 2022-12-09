var page1 = document.getElementById("page1");
var page2 = document.getElementById("page2");
var selectImageButton = document.getElementById("selectImageButton");
var selectCSVButton = document.getElementById("selectCSVButton");
var inputPlot = document.getElementById("inputPlot");
var inputPlotHarm = null;

async function onClick(event) {
    if (event.target.id == "selectImageButton") {
        event.target.disabled = true;
        selectCSVButton.disabled = true;
        let path = await eel.get_file_path(
            "Select Image",
            [["Image files", "*.png"], ["Image files", "*.jpg"]]
        )();
        if (path) {
            let result = await eel.create_input_plot(path, "Image")();
            inputPlotHarm = result[0]
            let json_data = result[1]
            if (inputPlot.style.display != "block") {
                document.getElementById("selectText").style.display = "none";
                mpld3.draw_figure("inputPlot", json_data);
                inputPlot.style.display = "block";
                document.getElementById("continueButton").disabled = false;
            } else {
                mpld3.draw_figure("inputPlot", json_data, false, true);
            }
        }
        event.target.disabled = false;
        selectCSVButton.disabled = false;
    } else if (event.target.id == "selectCSVButton") {
        event.target.disabled = true;
        selectImageButton.disabled = true;
        let path = await eel.get_file_path(
            "Select CSV File",
            [["CSV files", "*.csv"]]
        )();
        if (path) {
            let result = await eel.create_input_plot(path, "CSV")();
            inputPlotHarm = result[0]
            let json_data = result[1]
            if (inputPlot.style.display != "block") {
                document.getElementById("selectText").style.display = "none";
                mpld3.draw_figure("inputPlot", json_data);
                inputPlot.style.display = "block";
                document.getElementById("continueButton").disabled = false;
            } else {
                mpld3.draw_figure("inputPlot", json_data, false, true);
            }
        }
        event.target.disabled = false;
        selectImageButton.disabled = false;
    } else if (event.target.id == "continueButton") {
        page1.style.display = "none";
        page2.style.display = "block";
    } else if (event.target.id == "backButton") {
        page1.style.display = "block";
        page2.style.display = "none";
    } else if (event.target.id == "exitButton") {
        window.close()
    }
}

var popup = document.querySelector(".examplePopup");

async function onMouseUp(event) {
    if (popup.style.display == "block") {
        if (!popup.contains(event.target)) {
            popup.style.display = "none";
        }
    } else {
        if (event.target.id == "exampleText") {
            let rect = event.target.getBoundingClientRect();
            let top = rect.top - 256;
            let left = rect.left - 377;
            popup.style.top = top + "px";
            popup.style.left = left + "px";
            popup.style.display = "block";
        }
    }
}

var noOfPhasesElem = document.getElementById("noOfPhases");
var noOfSlotsElem = document.getElementById("noOfSlots");
var noOfPolesElem = document.getElementById("noOfPoles");
var chordedSlotsElem = document.getElementById("chordedSlots");
var outputPlot = document.getElementById("outputPlot");
var genPlotButton = document.getElementById("genPlotButton");
var exitButtonDiv = document.getElementById("exitButtonDiv")
var dynWarning = document.getElementById("dynWarning");

async function handleData() {
    let noOfPhases = noOfPhasesElem.value;
    let noOfSlots = noOfSlotsElem.value;
    let noOfPoles = noOfPolesElem.value;
    let chordedSlots = chordedSlotsElem.value;
    if (!(noOfPhases && noOfSlots && noOfPoles && chordedSlots)) {
        dynWarning.innerText = "Please fill in all the machine details.";
    } else if ((noOfSlots % noOfPhases != 0) || (noOfSlots / noOfPhases < 2)) {
        dynWarning.innerText = "Number of slots must be a multiple of the number of phases.";
    } else if (noOfSlots / (noOfPoles * noOfPhases) < 1) {
        dynWarning.innerText = "Number of slots per pole per phase cannot be less than one."
    } else if (chordedSlots >= Math.floor(noOfSlots / noOfPoles)) {
        dynWarning.innerText = "Winding cannot be chorded by more slots than are available per pole.";
    } else {
        let alpha = (180 * noOfPoles) / noOfSlots;
        let n = 180 / (noOfPhases * alpha);
        let rho = chordedSlots * alpha
        genPlotButton.disabled = true;
        dynWarning.innerText = "It is assumed that the windings are narrow spread.";
        let json_data = await eel.create_output_plot(inputPlotHarm, n, alpha, rho)();
        if (outputPlot.style.display != "block") {
            mpld3.draw_figure("outputPlot", json_data);
            outputPlot.style.display = "block";
            exitButtonDiv.style.display = "block";
        } else {
            mpld3.draw_figure("outputPlot", json_data, false, true);
        }
        genPlotButton.disabled = false;
    }
}

var warning1 = document.getElementById("warning1");
var warning2 = document.getElementById("warning2");

async function onMouseOver(event) {
    if (event.target.id == "selectCSVButton") {
        warning1.style.display = "none";
        warning2.style.display = "block";
    } else if (event.target.id == "selectImageButton") {
        warning1.style.display = "block";
        warning2.style.display = "none";
    }
}

document.addEventListener("click", onClick);
document.addEventListener("mouseup", onMouseUp);
document.addEventListener("mouseover", onMouseOver)
