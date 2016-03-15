var movieApp = angular.module('MovieApp', ['ngSanitize']);
var socket = io.connect('https://' + document.domain + ':' + location.port + '/movie');

movieApp.controller('SearchController', function($scope, $sce){
    
    $scope.name = '';
    $scope.text = '';
    $scope.searchResults = [];
    $scope.rating = '';
    $scope.rateResults = [];
    $scope.rateText = '';
    
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
            $scope.searchResults.push(results[i]);
            // $("searchResultsPanel").animate({
            //     height: '+=5em'
            // });
        }
        $scope.$apply();
        $scope.searchResults = [];
    });
    
    $scope.setName = function setName(){
      socket.emit('identify', $scope.name)  
    };
    
    socket.on('connect', function(){
       console.log('Connected'); 
    });
    
    
     $scope.rate = function rate(result){
        console.log('Rating: ', result);
        socket.emit('rate', result);
        $scope.text = '';
    };
    
    socket.on('rateResults', function(results){
        console.log("I am here");
        console.log(results[0]['text']);
         
        var text = '<input class="form-control" type="text" name="moviename"  value=' + '"' + results[0]['text'] +'">'
        $scope.rateText = $sce.trustAsHtml(text);
        console.log($scope.rateText);
        $scope.$apply();
        
    });
    
});

