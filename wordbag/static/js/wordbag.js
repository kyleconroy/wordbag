// An example Backbone application contributed by
// Load the application once the DOM is ready, using `jQuery.ready`:
var wordbag = {};

$(function(){

  var Letter = Backbone.Model.extend({});
  var Counter = Backbone.Model.extend({});
  var LetterList = Backbone.Collection.extend({});
  
  var letters = new LetterList();
  var counter = new Counter();
  
  var LetterView = Backbone.View.extend({

    tagName: "li",
    className: "letter",
    template: Handlebars.compile($("#letter-template").html()),
    
    events: {
      "click .remove": "remove",
    },
    
    initialize: function() {
      _.bindAll(this, 'render', 'remove');
      this.model.view = this;
    },
    
    remove: function(e) {
      e.preventDefault();
      letters.remove(this.model);
      $(this.el).remove();
    },

    render: function() {
      console.log(this.model.toJSON());
      $(this.el).html(this.template(this.model.toJSON()));
      return this;
    }

  });
  
  var CounterView = Backbone.View.extend({
    el: $("#counter"),
    
    initialize: function() {
      _.bindAll(this, 'render');
      this.model.view = this;
      this.model.bind("change", this.render);
    },
    
    render: function() {
      $(this.el).find("span").text(this.model.get("count"));
      return this;
    }
  });
    
  // Our overall **AppView** is the top-level piece of UI.
  var AppView = Backbone.View.extend({

    // Instead of generating a new element, bind to the existing skeleton of
    // the App already present in the HTML.
    el: $("#game"),

    // Delegated events for creating new items, and clearing completed ones.
    events: {
      "submit form": "draw"
    },

    // At initialization we bind to the relevant events on the `Todos`
    // collection, when items are added or changed. Kick things off by
    // loading any preexisting todos that might be saved in *localStorage*.
    initialize: function() {
      _.bindAll(this, 'render', 'draw');
      letters.bind("add", this.addOne);
    },

    draw: function(e) {
      e.preventDefault();
      
      if (letters.length >= 7)
        return false;
      
      var url = "/games/" + this.options.game + "/bag";
      
      $.ajax({
        url: url,
        type: "POST",
        dataType: "json",
        success: function(data, textStatus, jqXHR) {
          letters.add(data);
          counter.set({count: data.size});
        },
        error: function(jqXHR, textStatus, errorThrown) {
          console.log(textStatus)
        }
      });
    },
    
    addOne: function(letter) {
      var view = new LetterView({model: letter});
      $("#rack").append(view.render().el);
    },

    // Re-rendering the App just means refreshing the statistics -- the rest
    // of the app doesn't change.
    render: function() {
    }

  });
  
  wordbag.start = function(gameId) {
    new AppView({game: gameId});
    new CounterView({model: counter});
  }

});