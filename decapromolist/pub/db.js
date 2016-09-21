(function() {
    fileName = getParameterByName("list");
    if(fileName == null){
        fileName = "decapromolist.json";
    }

    var db = {
        loadData: function(filter) {
            setFilterValues(filter);
            prepareCategoryFilter(filter.sc);
            prepareStringFilter(filter.sx, filter.nm, filter.sz, filter.or); 
            var items = [];
            $.ajax({
              dataType: "json",
              url: fileName,
              async: false,
              success: function(data) {
                items = data;
              }
            });
            return $.grep(items, function(product) {
                try{
                    return (!filter.sx || checkString(product.sx, reSx))
                        && (!filter.sc || checkCategory(product.sc))
                        && (!filter.nm || checkString(product.nm, reNm))
                        && (!filter.sz || checkString(product.sz, reSz))
                        && (!filter.or || checkString(product.or, reOr))
                        && (!filter.pr || checkNumber(product.pr, filter.pr))
                        && (!filter.op || checkNumber(product.pp, filter.op))
                        && (!filter.dc || checkNumber(product.dc, filter.dc));
                } catch(err) {
                    console.log(err.message);
                    return false;
                }
            });
        },

        insertItem: function(insertingClient) { },

        updateItem: function(updatingClient) { },

        deleteItem: function(deletingClient) { }

    };

    window.db = db;

}());

var reNeg, rePos, reSx, reNm, reSz, reOr;

function prepareStringFilter(filterSx, filterNm, filterSz, filterOr){
    reSx = new RegExp(filterSx, "i");
    reNm = new RegExp(filterNm, "i");
    reSz = new RegExp(filterSz, "i");
    reOr = new RegExp(filterOr, "i");
}

function prepareCategoryFilter(filter){
    var negative = "";
    var positive = "";
    var strArray = filter.split("|");
    $.each(strArray, function(index, value) {
        if(value.substring(0,1).localeCompare("!") == 0){
            negative = negative + value.substring(1) + "|";
        }
        else {
            positive = positive + value + "|";
        }
    });
    negative = negative.substring(0, negative.length - 1);
    positive = positive.substring(0, positive.length - 1);
    if(negative.localeCompare("") != 0){
        reNeg = new RegExp(negative, "i");
    } else {
        reNeg = null;
    }
    if(positive.localeCompare("") != 0){
        rePos = new RegExp(positive, "i");
    } else {
        rePos = null;
    }
}

function checkString(string, re){
    return re.test(string);
}

function checkNumber(number, cmpNumber){
    var cmp = cmpNumber.substring(0,1);
    var num = parseFloat(number);
    if(cmp.localeCompare(">") == 0){
        var cmpNum = parseFloat(cmpNumber.substring(1));
        return num > cmpNum;  
    }
    else if(cmp.localeCompare("<") == 0){
        var cmpNum = parseFloat(cmpNumber.substring(1));
        return num < cmpNum;
    }
    else {
        var cmpNum = parseFloat(cmpNumber);
        return num == cmpNum; 
    }
}

function checkCategory(string){
    if(reNeg != null){
        if(reNeg.test(string)){
            return false;
        }
    }
    if(rePos != null){
        return rePos.test(string);
    }
    return true;
}

function getParameterByName(name, url){
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

function checkName(file) {
    var match = /decapromolist.*json/.test(file.name);
    return match;
}

function setFilterValues(filter) {
    if(!filterIsEmpty(filter)){
        localStorage.setItem("filter0", filter.sx);
        localStorage.setItem("filter1", filter.sc);
        localStorage.setItem("filter2", filter.nm);
        localStorage.setItem("filter3", filter.sz);
        localStorage.setItem("filter4", filter.op);
        localStorage.setItem("filter5", filter.pr);
        localStorage.setItem("filter6", filter.dc);
        localStorage.setItem("filter7", filter.or);
    }
}

function filterIsEmpty(filter){
    var array = $.map(filter, function(val, key) { return val; });
    for (var i = 0; i < array.length; i++) {
        if(array[i] != ""){
            return false;
        }
    }
    return true;
}

function insertFilterValues() {
    filterFields = document.getElementsByTagName("input");
    for(var i = 2; i < 10; i++){
        filterFields[i].value = localStorage.getItem("filter"+(i-2));
    }
    triggerEvent();
}

function generateUrl() {
    var i = 0;
    var params = "";
    if(getParameterByName("list") != null){
        params = params+"&list="+getParameterByName("list");    
    }
    params = params+"&sx="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&sc="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&nm="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&sz="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&op="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&pr="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&dc="+document.getElementsByTagName("input")[i+2].value;
    i++;
    params = params+"&or="+document.getElementsByTagName("input")[i+2].value;
    document.getElementById("genLink").href = "?"+params.substring(1);
}

function getFiltersFromUrl() {
    var array = [];
    var filter = false;
    filterFields = document.getElementsByTagName("input");
    array.push(getParameterByName("sx"));
    array.push(getParameterByName("sc"));
    array.push(getParameterByName("nm"));
    array.push(getParameterByName("sz"));
    array.push(getParameterByName("op"));
    array.push(getParameterByName("pr"));
    array.push(getParameterByName("dc"));
    array.push(getParameterByName("or"));
    for(var i = 0; i < 8; i++){
        if(array[i] != null){
            filterFields[i+2].value = array[i];
            filter = true;
        }
    }
    if(filter){
        triggerEvent();
    }
}

function triggerEvent(){
    var event = document.createEvent('Event');
    event.initEvent('keypress', true, false);
    event.which = 13;
    document.getElementsByTagName("input")[2].dispatchEvent(event);
}

