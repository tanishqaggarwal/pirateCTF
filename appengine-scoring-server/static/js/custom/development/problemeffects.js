function buyProblem(problemname) {
	$.ajax({
		url :"/buyer",
		method: "POST",
		data: {
			problemidentifier: problemname
		}
	}).done(function(data) {
		if ("invalid user cookie" == data || "invalid user object" == data)
			window.location.replace("/login");
		else if ("buying problems is not enabled" == data)
			$.notify("You can't buy problems in this CTF!","error");
		else if ("not a valid problem identifier" == data)
			$.notify("Oops, the problem isn't in our database!","error");
		else if ("at least parent problem not solved/bought" == data)
			$.notify("Gotta solve/buy at least one dependency.","error");
		else if ("already bought/solved" == data)
			$.notify("You already bought or solved this problem!","error");
		else if ("not enough points" == data)
			$.notify("You don't have enough points to buy this!","error");
		else {
			$.notify("You just bought this problem!","warning");
			$.notify("A possible flag was: " + data + "\n(click to dismiss)","warning");
			setTimeout(function () {
				location.reload();
			}, 3000);
		}
	});
}

function gradeProblem(problem,attempt,explanation) {
	$.ajax({
		url: "/grader",
		method: "POST",
		data: {
			problemidentifier: problem,
			attempt: attempt,
			explanation: explanation
		}
	}).done(function(data) {
		if ("invalid user cookie" == data || "invalid user object" == data)
			window.location.replace("/login");
		else if ("explanation required for flag submission" == data)
			$.notify("You have to submit an explanation!","error");
		else if ("not a valid problem identifier" == data)
			$.notify("Oops, the problem isn't in our database!","error");
		else if ("at least parent problem not solved/bought" == data)
			$.notify("Gotta solve/buy at least one dependency.","error");
		else if ("already solved" == data)
			$.notify("Your team already solved this problem!","error");
		else if ("already tried this" == data)
			$.notify("Your team already tried this answer!","error");
		else if ("incorrect" == data)
			$.notify("Incorrect!","error");
		else {
			$.notify("Correct!","success");
			setTimeout(function () {
				location.reload();
			}, 3000);
		}
	});
}

$("#problemdisplayswitcher").click(function() {
	var anchortext = $("#problemdisplayswitcher").text();
	if (anchortext == "View problem hierarchy viewer")
		$("#problemdisplayswitcher").text("View basic problem viewer");
		
	else
		$("#problemdisplayswitcher").text("View problem hierarchy viewer");
	$("#problemviewer").toggle();
	$("#hierarchy_container").toggle();
	$("#hierarchy_problem_viewer").html("");
});