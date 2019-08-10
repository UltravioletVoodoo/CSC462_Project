inputValue = document.getElementById("input-value")

function disableValue(){
    inputValue.disabled = true;
}

function enableValue(){
    inputValue.disabled = false;
}

inputValue.disabled = !document.getElementById("radio-set").checked