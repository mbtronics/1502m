<?php

# The file we use to store messages
$MessageFile = "messages.txt";

# The file in which we store the timestamp from the latest request
$TimestampFile = "timestamp.txt";

# The (arbitrary) message length
$MaxMessageLength = 100;

# User has submitted a message
if (Isset($_POST['message']))
{
	# Check for empty or to long messages
	$Message = trim($_POST['message']);
	if ($Message != "" && strlen($Message) <= $MaxMessageLength)
	{
		# Append message to file with newlne
		$Message .= "\n";
		file_put_contents($MessageFile, $Message, FILE_APPEND);
	}
}

# User has asked for new messages
if (Isset($_GET['messages']))
{
	# If file exists, print it and exit
	if (file_exists($MessageFile))	
	{
		echo file_get_contents($MessageFile);
		unlink($MessageFile);
	}

	# Write timestamp to file
	file_put_contents($TimestampFile, time());

	exit;
}

# User has asked DisplayClient status
if (Isset($_GET['status']))
{
	$Status = False;
	if (file_exists($TimestampFile))
	{
		# Read timestamp from file
		$Timestamp = intval(file_get_contents($TimestampFile));

		# Check if timestamp is less then 5s ago
		if ($Timestamp >= time()-5)
		{
			$Status = True;	# Last connection was less then 5s ago, status is good!
		}
	}

	if ($Status)
	{
		echo "online";
	}
	else
	{
		echo "offline";
	}

	exit;
}

# Client script has posted a livestream image
if (Isset($_FILES["live_jpg"]))
{
	move_uploaded_file($_FILES['live_jpg']['tmp_name'], $_FILES["live_jpg"]["name"]);
	exit;
}

?>
<!DOCTYPE html>
<html>

<head>
	<title>BUDA::lab Electronics Lab</title>
	<link rel="stylesheet" type="text/css" href="style.css">
	<link rel="stylesheet" type="text/css" href="led.css">
	<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.0/jquery.min.js"></script>
</head>

<body>
<!--
<div class="header">
	<img src="BUDALAB-LOGO7-300x102.png">
	<p><b><i>Electronics Lab</i></b></p>
</div>
-->
<div class="body">
	<div align="center">

		<p>Send messages to our 1502m LED display!</p>
		DisplayClient status: <span id="status">online</span>
		<div id="statusled" style="display: inline-block;" class="led led-green"></div> 

		<p>
			<input type="text" id="message" maxlength="<?php echo $MaxMessageLength; ?>" size="30">
			<input type="button" value="Submit" onClick="submitMessage();">
		</p>

		<canvas id="mjpeg" width="640px" height="480px" style="border:1px solid #d3d3d3"></canvas>
		<script language="JavaScript">
			var Mjpeg = document.getElementById('mjpeg').getContext('2d');
			var Img = new Image();

			Img.onload = function() {
				Mjpeg.drawImage(Img, 0, 0);
		  	};

		  	Img.src = "live.jpg";

			window.setInterval("doTimedStuff()", 500);

			function doTimedStuff() {
				refreshCanvas();
				updateStatus();
			};

			function refreshCanvas() {
				Img.src = "live.jpg?" + Date.now();
				Mjpeg.drawImage(Img, 0, 0);
			};

			function updateStatus() {
				jQuery.get("<?php echo $_SERVER['PHP_SELF']; ?>?status&" + Date.now(), function(response) {
					$("#status").html(response);
					if (response == "online") {
						$("#statusled").removeClass('led-red');
						$("#statusled").addClass('led-green');
					}
					else
					{
						$("#statusled").removeClass('led-green');
						$("#statusled").toggleClass('led-red');
					}
				});
			};

			function submitMessage() {
				jQuery.post("<?php echo $_SERVER['PHP_SELF']; ?>",{message: $("#message").val()});
			};
		</script>
	</div>
</div>

</body>

</html>
