var movieApp = angular.module('MovieApp', ['ngSanitize']);
var socket = io.connect('https://' + document.domain + ':' + location.port + '/movie');

movieApp.controller('SearchController', function($scope, $sce){
    
    $scope.name = '';
    $scope.text = '';
    $scope.searchResults = [];
    $scope.rating = '';
    $scope.rateResults = [];
    $scope.rateText = '';
    $scope.movieGenres = [];
    $scope.year = '';
    $scope.recommendationResults = []
    
    $scope.search = function search(){
        console.log('Search result: ', $scope.text);
        socket.emit('search', $scope.text);
        $scope.text = '';
    };
    
    socket.on('searchResults', function(results){
        if (results.length > 0) {
            $("#searchResultsPanel").show();
        }
        else {
            $("#searchResultsPanel").hide();
        }
        for(var i = 0; i < results.length; i++){
            console.log(results[i]);
            console.log(results[i]['genres']);
            $scope.searchResults.push(results[i]);
            var genreString = "";
            for(let genre of results[i]['genres']){
                genreString +=  genre + ", ";
            }
            var newStr = genreString.substring(0, genreString.length-2);
            console.log(newStr);
            results[i]['genres'] = newStr;
        }
        $scope.$apply();
        $scope.searchResults = [];
    });
    
    $scope.recommend = function recommend(){
        console.log("I get here");
        socket.emit('recommend', 'recommend');
    };
    
    socket.on('recommendationResults', function(results){
        $("#recommendationModal").modal('show');
        for(var i = 0; i < results.length; i++){
            console.log(results[i]);
            
            $scope.recommendationResults.push(results[i]);
            
        }
        $scope.$apply();
    });
    
    $scope.setName = function setName(){
      socket.emit('identify', $scope.name)  
    };
    
    socket.on('connect', function(){
       console.log('Connected'); 
    });
    
    $scope.rate = function rate(result){
        console.log('Rating: ', result);
        
        console.log(result);
        $("#searchModal").modal('hide');
        
        var text = '<input class="form-control" type="text" name="moviename" id="moviename" value=' + '"' + result['text'] +'">'
        var yearText = '<input class="form-control" type="hidden" name="movieyear" id="movieyear" value=' + '"' + result['year'] +'">'
        console.log(text);
        $scope.rateText = $sce.trustAsHtml(text);
        $scope.year = $sce.trustAsHtml(yearText);
        console.log($scope.rateText);
        $("#rateModal").modal('show');
        $scope.text = '';
    };
    
    
    
});


