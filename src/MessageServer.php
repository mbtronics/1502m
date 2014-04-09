<?php

$MessageFile = "messages.txt";

if (Isset($_POST['submit']))
{
	$Message = $_POST['message'] . "\n";
	file_put_contents($MessageFile, $Message, FILE_APPEND);
}

if (Isset($_GET['messages']))
{
	if (file_exists($MessageFile))	
	{
		echo file_get_contents($MessageFile);
		unlink($MessageFile);
	}

	exit;
}

?>

<html>

<head>
</head>

<body>

<form method="POST" action="<?php echo $_SERVER['PHP_SELF']; ?>">
	<input type="text" name="message"><br>
	<input type="submit" name="submit" value="Submit">
</form>

</body>

</html>
