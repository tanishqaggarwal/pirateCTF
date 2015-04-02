function quicksort(thearray,value) {

	function partition(items, left, right, value) {

		function swap(items, firstIndex, secondIndex){
		    var temp = items[firstIndex];
		    items[firstIndex] = items[secondIndex];
		    items[secondIndex] = temp;
		}

	    var pivot   = items[Math.floor((right + left) / 2)][value],
	        i       = left,
	        j       = right;
	    while (i <= j) {
	        while (items[i][value] < pivot) {
	            i++;
	        }
	        while (items[j][value] > pivot) {
	            j--;
	        }
	        if (i <= j) {
	            swap(items, i, j);
	            i++;
	            j--;
	        }
	    }
	    return i;
	}

	var index;

    if (thearray.length > 1) {
        index = partition(thearray, 0, thearray.length - 1,value);
        if (0 < index - 1) {
            quickSort(thearray, 0, index - 1);
        }
        if (index < thearray.length - 1) {
            quickSort(thearray, index, thearray.length - 1);
        }
    }

    return thearray;
}

var ScoreBoard = function(data,scoreboardid,chartid,solvedtableid) {
	this.scoreboardid = scoreboardid;
	this.chartid = chartid;
	this.solvedtableid = solvedtableid;
	//format the data so that the date strings are now in Javascript format
	data['data'].forEach( function(team) {
		team['time'] = Date.parse(team['time']);
	});
	this.scoreboarddata = data['data'];
	this.sortdata();
}

ScoreBoard.prototype.sortdata = function() {
	//This function produces the score board.
	var sortedbypoints = quicksort(this.scoreboarddata,"points");

	//sort by time now
	var beginConsecutiveSeries = 0;
	for (var i = 0; i < this.scoreboarddata.length; i++) {
		if (i == this.scoreboarddata.length - 1) {
			if (this.scoreboarddata[i - 1].p != this.scoreboarddata[i].p) {
				var newarray = this.scoreboarddata.slice(beginConsecutiveSeries,i);
				quicksort(newarray,"time");
				for (var j = beginConsecutiveSeries; j < i; j++) {
					this.scoreboarddata[j] = newarray[j - beginConsecutiveSeries];
				}
			}
			else {
				var newarray = this.scoreboarddata.slice(beginConsecutiveSeries,i + 1);
				quicksort(newarray,"time");
				for (var j = beginConsecutiveSeries; j < i + 1; j++) {
					this.scoreboarddata[j] = newarray[j - beginConsecutiveSeries];
				}
			}
		}
		else if (this.scoreboarddata[i + 1].p != this.scoreboarddata[i].p) {
			var newarray = this.scoreboarddata.slice(beginConsecutiveSeries,i + 1);
			quicksort(newarray,"time");
			for (var j = beginConsecutiveSeries; j < i + 1; j++) {
				this.scoreboarddata[j] = newarray[j - beginConsecutiveSeries];
			}
		}
		else {
			beginConsecutiveSeries += 1;
		}
	}

	var leftsidebigger = false;
	//Now that we're all sorted, let's check to see which side is bigger. make sure the left is bigger-body:
	if (this.scoreboarddata[0].p >= this.scoreboarddata[this.scoreboarddata.length - 1].p) {
		leftsidebigger = true;
	}
	if (!leftsidebigger) {
		this.scoreboarddata.reverse();
	}
}


//Concern: does the scoreboardinstance actually refer to the ScoreBoard instance?
ScoreBoard.prototype.producetable = function () {

	function sanitize(text) {
		text = text.substring(1,257);
		var sanitizedtext = text.replace("<","&lt;");
		sanitizedtext = sanitizedtext.replace(">","&gt;");
		return sanitizedtext;
	}

	var scoreboardinstance = this;

	for(var i = 0; i < this.scoreboarddata.length; i++) {
		$("#" + this.scoreboardid + " tr:last").after("<tr><a id = " + toString(i) + "><td></td><td>" + str(i + 1) + "</td><td>" + sanitize(this.scoreboarddata[i].teamname) + "</td><td>" + sanitize(this.scoreboarddata[i].school) + "</td><td>" + sanitize(this.scoreboarddata[i].points) + "</td></a></tr>");
		$("#" + toString(i)).click(function () {
			scoreboardinstance.producesolvedtable(this.scoreboarddata[i].teamname);
		});
}

ScoreBoard.prototype.producechart = function () {
	var chartseries = [];
	var NUM_TOP_SERIES = 10;

	//Get top 10 successful attempts
	for (var i = 0; i < NUM_TOP_SERIES; i++) {
		var theteamname = this.scoreboarddata[i].teamname;
		$.ajax({
			method: "POST",
			url: "/showteamproblems",
			data: {
				teamname : theteamname,
			},
		}).done( function (responseobj) {
			var attemptsobject = JSON.parse(responseobj);
			var attemptsarray = [];
			attemptsobject.forEach( function (obj) {
				obj['time'] = Date.parse(obj['time']);
				obj.pop('title');
				obj.pop('problem_parents');
				obj.pop('problem_children');
				attemptsarray.push(obj);
			});
			attemptsarray = quicksort(attemptsarray,"time");
			var rightsidebigger = false;
			//Now that we're all sorted, let's check to see which side is bigger. make sure the right is bigger-body:
			if (attemptsarray[0]['time'] <= attemptsarray[attemptsarray.length - 1]['time']) {
				rightsidebigger = true;
			}
			if (!rightsidebigger) {
				this.scoreboarddata.reverse();
			}

			//The below construct may vary based on the chart library used.
			var topush = {
				teamname: theteamname,
				data: [],
			}

			for (var j = 0; j < attemptsarray.length; j++) {
				if (j == 0) {
					var points = attemptsarray[i].points;
					if (attemptsarray.buyed == true) {
						points = attemptsarray[i].points - attemptsarray[i].buy_for_points;
					}
					topush['data'].push([attemptsarray[i].time,points]);
				}
				else {
					var currentpoints = attemptsarray[i].points;
					if (attemptsarray[i].buyed == true) {
						currentpoints = attemptsarray[i].points - attemptsarray[i].buy_for_points;
					}
					var previouspoints = topush['data'][i - 1].points;
					topush['data'].push([attemptsarray[i].time,points + previouspoints]);
				}
			}
			chartseries.push(topush);
			if (i == NUM_TOP_SERIES - 1) {
				//Now that all data has been pushed to the chart series, produce the actual chart using the chartseries variable.
			}
		});
	}
}

ScoreBoard.prototype.producesolvedtable = function(theteamname) {
	$.ajax({
		method: "POST",
		url: "/showteamproblems",
		data: {
			teamname: theteamname
		},
	}).done(function (responseobj) {
		var data = JSON.parse(responseobj);
		//Produce table data right here using this.solvedtableid
		//Hide scoreboard table, display the solved table here
		$("")
	});
}