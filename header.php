<!doctype html>

<html lang="en">

<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    
    <!--Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6" crossorigin="anonymous">
    <!--Custom CSS -->
    <link href="styles.css" rel="stylesheet">
    <title>
        <?php
            //echo $page;
            
            switch ($page) {
                case "default":
                    echo "Gaultney Management LLC";
                    break;
                case "app":
                    echo "Fill Out An Application";
                    break;
                case "test":
                    echo "Playground / Sandbox / Whatever";
                    break;
                case "captionVote":
                    echo "POTW: Vote On Your Favorite Caption";
                    break;
                case "CurrentProblems":
                    echo "POTW: This Week's Math Problems";
                    break;
                case "LastWeekSolutions":
                    echo "POTW: Last Week's Solutions";
                    break;
                case "MathArchive":
                    echo "POTW: Problem and Solution Archive";
                    break;
            }
        ?>
    </title>
</head>

<body>

<nav class="navbar navbar-expand-sm navbar-dark bg-info">
    <div class="mx-auto d-sm-flex d-block flex-sm-nowrap">
        <a class=" text-dark navbar-brand" href="index.php">Gaultney Management LLC</a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarsExample11" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <!-- <div class="collapse navbar-collapse text-center" id="navbarsExample11">
            <ul class="navbar-nav">
                <li class="nav-item active">
                    <a class="nav-link" href="#">Link</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Link</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Link</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Link</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="#">Link</a>
                </li>
            </ul>
        </div> -->
    </div>
</nav>

<div class="container">