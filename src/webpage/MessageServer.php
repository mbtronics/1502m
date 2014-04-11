<?php

# The file we use to store messages
$MessageFile = "messages.txt";

# The (arbitrary) message length
$MaxMessageLength = 100;

# User has submitted the form
if (Isset($_POST['submit']))
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
</head>

<body>

<div class="header">
	<img src="BUDALAB-LOGO7-300x102.png">
	<p><b><i>Electronics Lab</i></b></p>
</div>

<div class="body">
	<div align="center">
		<p>Send messages to our 1502m LED display!</p>
		<form method="POST" action="<?php echo $_SERVER['PHP_SELF']; ?>">
			<input type="text" name="message" maxlength="<?php echo $MaxMessageLength; ?>" size="30">
			<input type="submit" name="submit" value="Submit">
		</form>
		<br>
		<canvas id="mjpeg" width="640px" height="480px" style="border:1px solid #d3d3d3"></canvas>
		<script language="JavaScript">
			var Mjpeg = document.getElementById('mjpeg').getContext('2d');
			var Img = new Image();

			Img.onload = function() {
				Mjpeg.drawImage(Img, 0, 0);
		  	};

		  	Img.src = "live.jpg";

			window.setInterval("refreshCanvas()", 500);
			function refreshCanvas(){
				Img.src = "live.jpg?" + Date.now();
				Mjpeg.drawImage(img, 0, 0);
			};
		</script>
	</div>
</div>

</body>

</html>
