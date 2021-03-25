<script>
	import Lane from "./Lane.svelte";

	let farRight = [
		{
			id: 1,
			text: `OAN (Home)`,
			url: `https://www.oann.com/category/newsroom/feed`,
		},
		{
			id: 2,
			text: `Breitbart (Home)`,
			url: `http://feeds.feedburner.com/breitbart`,
		},
		{
			id: 3,
			text: `New York Post (Home)`,
			url: `https://nypost.com/feed/`,
		},
	];

	let right = [
		{
			id: 1,
			text: `Fox News (National)`,
			url: `http://feeds.foxnews.com/foxnews/national`,
		},
		{
			id: 2,
			text: `Newsmax (Home)`,
			url: `https://www.newsmax.com/rss/Newsfront/16`,
		},
	];

	let center = [
		{
			id: 1,
			text: `NPR (Home)`,
			url: `http://www.npr.org/rss/rss.php?id=1001`,
		},
		{
			id: 2,
			text: `Reuters (U.S.)`,
			url: `https://www.reutersagency.com/feed/?best-regions=north-america&post_type=best`,
		},
		{
			id: 3,
			text: `The BBC (World)`,
			url: `http://feeds.bbci.co.uk/news/rss.xml`,
		},
	];

	let left = [
		{
			id: 1,
			text: `The New York Times (Home)`,
			url: `https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml`,
		},
		{
			id: 2,
			text: `The Washington Post (National)`,
			url: `http://feeds.washingtonpost.com/rss/national?itid=lk_inline_manual_39`,
		},
		{
			id: 3,
			text: `The Guardian (World)`,
			url: `https://www.theguardian.com/world/rss`,
		},
	];

	let farLeft = [
		{ id: 1, text: `Jacobin (Home)`, url: `https://jacobinmag.com/feed` },
		{ id: 2, text: `Vox (Home)`, url: `https://www.vox.com/rss/index.xml` },
		{
			id: 2,
			text: `BuzzfeedNews (Home)`,
			url: `https://www.buzzfeed.com/index.xml`,
		},
	];
</script>

<main>
	<h1>Pop the Bubble News</h1>
	<h5>
		A simple RSS feed dashboard to quickly view the full spectrum of news in
		the U.S.
	</h5>
	<div class="scrolling-wrapper">
		<div class="lanes">
			<p class="header">Left</p>
			<p class="header">Left-leaning</p>
			<p class="header">Center</p>
			<p class="header">Right-leaning</p>
			<p class="header">Right</p>
		</div>
		<div class="lanes">
			<div class="farleft lane">
				<Lane class="farleft" rssOptions={farLeft} />
			</div>
			<div class="left lane"><Lane rssOptions={left} /></div>
			<div class="center lane"><Lane rssOptions={center} /></div>
			<div class="right lane"><Lane rssOptions={right} /></div>
			<div class="farright lane"><Lane rssOptions={farRight} /></div>
		</div>
	</div>
	<div class="about">
		<p>
			I often find myself wondering how people can live in such entirely
			different realities. One commonly discussed idea is that of online
			"bubbles", where we only consume news from certain sources and only
			talk about it with like-minded people. These bubbles often reinforce
			our prior beliefs and further distance us from those in other
			bubbles. One small way to help bridge this gap is to simply be aware
			of the full spectrum of news available to us. I've tried doing this
			by following a variety of accounts on Twitter, but there is so much
			noise on that platform.
		</p>
		<p>
			In response, I made this super simple news dashboard. It is divided
			into five columns, ranging from one end of the political spectrum to
			the other (as defined by
			<a href="https://www.allsides.com/media-bias/media-bias-ratings"
				>AllSides research</a
			>). Each lane lists the top 10 news stories from an RSS feed of that
			news source, and you can click the headline to visit the source
			article to read further. You can also click on the news source name
			(try clicking on "Vox (Home)") to select a different news source.
			With this tool, you can get an idea of what news is disseminated
			across the political spectrum at a quick glance. In short, you can
			pop the bubble.
		</p>
	</div>
</main>

<style>
	.farleft {
		background-color: #99aeff33;
	}

	.left {
		background-color: #cce1ff33;
	}

	.farright {
		background-color: #ffadb633;
	}

	.right {
		background-color: #ffe0e933;
	}

	.lane {
		max-width: 300px;
		min-width: 250px;
		margin: 0 auto;
		padding: 0 10px;
		border: 1px solid lightgrey;
	}

	.header {
		max-width: 300px;
		min-width: 200px;
		margin: 0 auto;
		padding: 0 10px;
		color: #555555;
	}

	.about {
		color: #777777;
		font-weight: 1;
		text-align: center;
		width: 80%;
		margin: 50px auto;
	}

	main {
		text-align: center;
		padding: 1em;
		margin: 0 auto;
		background-color: transparent;
	}

	.lanes {
		display: flex;
	}

	.scrolling-wrapper {
		overflow-x: scroll;
		-webkit-overflow-scrolling: touch;
	}

	h1 {
		color: #111111;
		font-size: 2em;
		font-weight: 10;
	}

	h5 {
		color: #555555;
		font-size: 1em;
		font-weight: 5;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
