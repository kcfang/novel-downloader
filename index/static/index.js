
var Index = React.createClass({
    render: function() {
    	return (<div className="container">
    		<h1>卡提諾小說轉換器 v1</h1>
    		<InputForm />
    		</div>
	       )
    }
});

var Result = React.createClass({
    render: function() {
    	return (<div className="container">
    		<p>debug</p>
    		</div>
	       )
    }
});

var InputForm = React.createClass({
    getInitialState: function() {
        var id = this.getID();
        return {mobi: [], show:false, wait: false, id: id, error_msg: ""};
    },
    getID: function(){
        return Math.random().toString(36).substring(7);
    },
    genMobi: function(){
        this.setState({wait: true});
        var timer = setInterval(this.getlog, 5000);
        $.ajax({
            url: "../api/genMobi/",
            dataType: 'json',
            type: 'GET',
            data: {url: this.state.url, page: this.state.page, id: this.state.id },
            success: function(data) {
                console.log(data);
                if ("fail_msg" in data) {
                    this.setState({error_msg: data.fail_msg, wait: false});
                } else {
                    this.setState({mobi: data.mobi, show: true, wait: false});
                }
                clearInterval(timer);
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        }); 
    },
    getlog:function(){
        $.ajax({
            url: "../api/log/",
            dataType: 'json',
            type: 'GET',
            data: {id: this.state.id },
            success: function(data) {
                console.log(data);
                if("success" in data){
                    clearInterval(timer);
                    this.setState({log: ""});
                    return true;
                }
                this.setState({log: data.log});
            }.bind(this),
            error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
                clearInterval(timer);
            }.bind(this)
        }); 
    },
    urlChange: function(e){
        this.setState({url: e.target.value});
    },
    pageChange: function(e){
        this.setState({page: e.target.value});
    },
    clearAll: function(e){
        this.setState({page: "", url: ""});
    },

    render: function() {
        if(this.state.show){
            var result = [];
            var mobi = this.state.mobi.map(function(mobi, idx) {
                var path= window.location.href + ".." + mobi;
                return <div><a href={path}><p className="text-success">{path.split('/').reverse()[0]}</p></a></div>
            });
            result.push(<h2> Donwload link </h2>);
            result.push(mobi);
        }
        if (this.state.wait) {
            var result = [];
            result.push(<h4>Loading... please wait... </h4>);
            var logs = this.state.log.map(function(text, idx){
                return <p>{text}</p>
            });
            result.push(<div>{logs}</div>);
        }

        if (this.state.error_msg) {
            var result = [];
            result.push(<div><h3>{this.state.error_msg}</h3></div>);
        }

    	return (
	    <div>
	    <div className="form-group">
		<label for="url">ck101 url</label>
		<input className="form-control" id="url" placeholder="www.ck101.com/thread-3365281-1-1.html" onChange={this.urlChange} value={this.state.url}></input>
	    </div>
	    <div className="form-group">
		<label for="page">Split page</label>
		<input className="form-control" id="page" placeholder="How many pages you want to split this novel? (default 30)" onChange={this.pageChange} value={this.state.page}></input>
	    </div>
            <div>
	    <button type="button" className="btn btn-primary" onClick={this.genMobi}>Submit</button>
	    <button type="button" className="btn btn-default" onClick={this.clearAll}>Clear</button>
	    </div>
            {result}
	    </div>
	   )
    }
});

ReactDOM.render(
    <Index />,
    document.getElementById('index')
);
