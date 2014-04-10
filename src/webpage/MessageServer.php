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
		<img src="LEDdisplay.jpg">
	</div>
</div>

</body>

</html>
