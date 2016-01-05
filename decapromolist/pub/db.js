(function() {

    var db = {
        loadData: function(filter) {
            var items = [];
            $.ajax({
              dataType: "json",
              url: "decapromolist.json",
              async: false,
              success: function(data) {
                items = data;
              }
            });
            return $.grep(items, function(product) {
                try{
                    return (!filter.sx || checkString(product.sx, filter.sx))
                        && (!filter.sc || checkString(product.sc, filter.sc))
                        && (!filter.nm || checkString(product.nm, filter.nm))
                        && (!filter.sz || checkString(product.sz, filter.sz))
                        && (!filter.or || checkString(product.or, filter.or))
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

function checkString(string, searchValue) {
    var result = false;
    var strArray = searchValue.split("|");
    $.each(strArray, function(index, value) {
        if(result) {
            return result; 
        } 
        result = string.toLowerCase().indexOf(value.toLowerCase()) > -1;
    });
    return result;
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

