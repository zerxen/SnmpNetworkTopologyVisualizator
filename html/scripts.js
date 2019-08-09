// ####################################
// # replaces content of specified DIV
// ####################################
function printToDivWithID(id,text){
  div = document.getElementById(id);
  div.innerHTML += text;
}

function cleanDivWithID(id){
  div = document.getElementById(id);
  div.innerHTML = "";
}

function OnClickLinkDetails(source_name, target_name, source_indexes, target_indexes ){

    console.log(source_name.id)
    console.log(source_indexes)
    console.log(target_name.id)
    console.log(target_indexes)

    cleanDivWithID("infobox")
    cleanDivWithID("infobox_header")

    printToDivWithID("infobox_header",source_name.id + " - " + target_name.id + "<br>")
    printToDivWithID("infobox_header","<img src=\"img/site/LeftPanelSeparation.png\">")

    targetdiv = document.getElementById("infobox")

    //# SIMPLIFIED GRAPH PRINTING
    for (var index of source_indexes){
        console.log("index " + index + " on " + source_name.id)
        var filename = "data/stats/" + source_name.id + "_" + index + ".json"
        console.log("filename: " + filename)
        readTextFile(filename, function(text){
            var interface = JSON.parse(text);
            console.log(interface)
            var iDivGraph = document.createElement('div');
            iDivGraph.id = source_name.id + "_" + interface['ifDescr'] + "_graph";
            targetdiv.appendChild(iDivGraph);

            draw_device_interface_graphs_to_div(interface,source_name.id, targetdiv)
        });
    }

    //# SIMPLIFIED GRAPH PRINTING
    for (var index of target_indexes){
        console.log("index " + index + " on " + target_name.id)
        var filename = "data/stats/" + target_name.id + "_" + index + ".json"
        console.log("filename: " + filename)
        readTextFile(filename, function(text){
            var interface = JSON.parse(text);
            console.log(interface)
            var iDivGraph = document.createElement('div');
            iDivGraph.id = target_name.id + "_" + interface['ifDescr'] + "_graph";
            targetdiv.appendChild(iDivGraph);

            draw_device_interface_graphs_to_div(interface,target_name.id, targetdiv)
        });
    }


}

// ###################################
// # Graph Drawing Functions         #
// ###################################

// This draws a single specific interface to div
function draw_device_interface_graphs_to_div(interface,deviceid, targetdiv){

        //console.log("Interface: ")
        //console.log(interface)

        var iDiv = document.createElement('div');
        iDiv.id = deviceid + "_" + interface['ifDescr'] + "_graph_header";
        iDiv.align = 'left';
        iDiv.innerHTML = "<br>" + deviceid + " - " + interface['ifDescr'];
        targetdiv.appendChild(iDiv);

        var iDivGraph = document.createElement('div');
        iDivGraph.id = deviceid + "_" + interface['ifDescr'] + "_graph";
        targetdiv.appendChild(iDivGraph);

        //var TimeStampStrings = ["x2001", "x2002", "x2003", "x2004", "x2005", "x2006", "x2007", "x2008", "x2009", "x2010", "x2011", "x2013"]
        //var InOctetsData = [74, 82, 80, 74, 73, 72, 74, 70, 70, 66, 66, 69];
        //var OutOctetsData = [14, 8, 78, 74, 24, 2, 7, 40, 76, 100, 78, 12];
        var TimeStampStrings = []
        var InOctetsData = []
        var OutOctetsData = []

        for (var stats of interface['stats']){
            TimeStampStrings.push(stats['time'])
            InOctetsData.push(stats['InSpeed'])
            OutOctetsData.push(stats['OutSpeed'])
            //console.log(TimeStampStrings)
            //console.log(InOctetsData)
            //console.log(OutOctetsData)
        }

        draw_graph_from_data_to_div(InOctetsData,OutOctetsData,TimeStampStrings,iDivGraph)

}

// This draws all interfaces from device to div
function draw_device_graphs_to_div(deviceid, data, targetdiv){

    for (var interface of data[deviceid]['interfaces']){
        draw_device_interface_graphs_to_div(interface,deviceid, targetdiv)
    }
}


function draw_graph_from_data_to_div(InOctetsData,OutOctetsData,TimeStampStrings,iDivGraph){


    traceOut = {
      type: 'scatter',
      x: TimeStampStrings,
      y: OutOctetsData,
      mode: 'lines',
      name: 'Out',
      line: {
        color: 'rgb(219, 64, 82)',
        width: 3
      }
    };

    traceIn = {
      type: 'scatter',
      x: TimeStampStrings,
      y: InOctetsData,
      mode: 'lines',
      name: 'In',
      line: {
        color: 'rgb(55, 128, 191)',
        width: 1
      }
    };

    var layout = {
      // title:'Adding Names to Line and Scatter Plot',
      margin: {
        autoexpand: true,
        l: 35,
        r: 20,
        t: 5,
        b: 35
      },
      width: 600,
      height: 150,
      xaxis: {
        title: 'Time',
        showgrid: true,
        zeroline: true,
        showline: true
      },
      yaxis: {
        title: 'Mbps',
        showline: true,
        showtickprefix: 'first'
      },
      paper_bgcolor: 'rgba(255,255,255,0.7)',
      plot_bgcolor: 'rgba(0,0,0,0)'
    };

    var data = [traceOut, traceIn];

    Plotly.newPlot(iDivGraph, data, layout, {showSendToCloud: false});

}