<?php
require_once("functions.php");
				$dblink=db_connect("contact_data");
if (!isset($_GET['page']))
	redirect("index.php?page=login&errMsg=InvalidSid");
else
{
	$sid=$_GET['sid'];
	$sql="Select `auto_id` from `accounts` where `sid`='$sid'";
	$result=$dblink->query($sql) or 
		die ("Something went wrong with $sql".$dblink->error);
	if($result->num_rows<=0)//no valid/current sid found\
		redirect("index.php?page=login&errmsg=InvalidSid");
	else{
		?>

<head>
	<script src="assets/js/jquery-3.5.1.js"></script>
<link href="assets/css/bootstrap.css" rel="stylesheet">
</head>
<body>
<div class="panel panel-default">
	<div class="panel-heading">Database Entries</div>
	<div class="panel-body">
		<div class="table-responsive">
		<table class="table table-striped">
		<thead>
			<tr>
			<th>First Name</th><th>Last Name</th><th>Email</th><th>Phone</th><th>Comments</th>
			</tr>
			</thead>
			<tbody id="results">
				<?php
				
				$sql="Select `first_name`,`last_name`,`email`,`phone`,`comments` from `contact_info`";
				$results=$dblink->query($sql) or 
					die("somethign went wrong with $sql".$dblink->error);
				while ($data=$results->fetch_array(MYSQLI_ASSOC))
				{
					echo '<tr>';
					echo '<td>'.$data['first_name'].'</td>';
					echo '<td>'.$data['last_name'].'</td>';
					echo '<td>'.$data['email'].'</td>';
					//echo '<td>'.$data['user_name'].'</td>';
					//echo '<td>'.$data['password'].'</td>';
					echo '<td>'.$data['phone'].'</td>';
					echo '<td>'.$data['comments'].'</td>';
				echo '</tr>';
				}
				?>
			</tbody>
			</table>
		</div>
	</div>
	</div>
	<script>
	function refresh_data(){
		$.ajax({
			type: 'get',
			url:'QUERY_contacts.php',
			success: function(data) {
				$('#results').html(data);//document.getElementById('results').innerHTML=data;
			}
		});
	}
		setInterval(refresh_data, 500);
	</script>
</body>
<?php
	}
}
		?>