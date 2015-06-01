<?php
# The file we use to store messages
$MessageFile = "messages.txt";

# Logfile
$LogFile = "log.txt";

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
		$LogMessage = date('d/m/Y h:i:s') . " " . $Message;
		file_put_contents($LogFile, $LogMessage, FILE_APPEND);
	}
	exit;
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

	exit;
}

# User has asked DisplayClient status
if (Isset($_GET['status']))
{
	$Status = False;
	if (file_exists("live.jpg"))
	{
		$Timestamp = filemtime("live.jpg");

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

if (Isset($_GET['log']))
{
	if (file_exists($LogFile))
	{
		echo file_get_contents($LogFile);
	}
	exit;
}

if (Isset($_POST['clearlog']))
{
	unlink($LogFile);
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

<div class="header">
	<img src="BUDALAB-LOGO7-300x102.png">
	<p><b><i>Electronics Lab</i></b></p>
</div>

<div class="body">
	<div align="center">

		<p>Send messages to our 1502m LED display!</p>
		DisplayClient status: <span id="status">online</span>
		<div id="statusled" style="display: inline-block;" class="led led-green"></div> 

		<p>
			<input type="text" id="message" maxlength="<?php echo $MaxMessageLength; ?>" size="30">
			<input type="button" value="Submit" onClick="submitMessage();">
		</p>

		<table border="0">
			<tr>
				<td>
					<canvas id="mjpeg" width="640px" height="480px" style="border:1px solid #d3d3d3"></canvas>
				</td>
				<td>
					<center><h2>Log: <!--<input type="button" value="Clear log" onClick="clearLog();">--></h2></center><textarea id="log" rows="28" cols="50" disabled="1" wrap="off"></textarea>
				</td>
			</tr>
		</table>
		
		<script language="JavaScript">
			var Mjpeg = document.getElementById('mjpeg').getContext('2d');
			var Img = new Array();
			var DisplayBuf = 0;
			var NumBuffers = 5;
			var LoadBuf = NumBuffers-1;

			for (i=0; i<NumBuffers; i++) {
				Img[i] = new Image();
			}
			
			window.setInterval("doTimedStuff()", 500);

			function doTimedStuff() {
				refreshCanvas();
				updateStatus();
			};

			function refreshCanvas() {
				Img[LoadBuf].src = "live.jpg?" + Date.now();
				Mjpeg.drawImage(Img[DisplayBuf], 0, 0);

				LoadBuf++;
				if (LoadBuf==NumBuffers) {
					LoadBuf=0;
				}

				DisplayBuf++;
				if (DisplayBuf==NumBuffers) {
					DisplayBuf=0;
				}

				console.log("Load " + LoadBuf + " Disp " + DisplayBuf)
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

				jQuery.get("<?php echo $_SERVER['PHP_SELF']; ?>?log&" + Date.now(), function(response) {
					$("#log").val(response.split("\n").reverse().join("\n"));	
				});
			};

			function submitMessage() {
				jQuery.post("<?php echo $_SERVER['PHP_SELF']; ?>",{message: $("#message").val()});
			};

			function clearLog() {
				jQuery.post("<?php echo $_SERVER['PHP_SELF']; ?>",{clearlog: true});
			};
		</script>
	</div>
</div>

</body>

</html>
