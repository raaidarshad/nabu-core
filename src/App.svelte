<script>
	import Lane from "./Lane.svelte";
	import About from "./About.svelte";
	import Contact from "./Contact.svelte";
	import Footer from "./Footer.svelte";
	import Header from "./Header.svelte";
	import Support from "./Support.svelte";

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
	<div class="maincontent">
		<Header />
		<h1>Pop the Bubble News</h1>
		<h5>
			A simple RSS feed dashboard to quickly view the full spectrum of
			news in the U.S.
		</h5>
		<div class="scrolling-wrapper">
			<div class="lanes">
				<div class="lane">
					<Lane class="farleft" rssOptions={farLeft} title="Left" bgcolor="#99aeff33"/>
				</div>
				<div class="lane"><Lane rssOptions={left} title="Left-leaning" bgcolor="#cce1ff33"/></div>
				<div class="lane"><Lane rssOptions={center} title="Center"/></div>
				<div class="lane"><Lane rssOptions={right} title="Right-leaning" bgcolor="#ffe0e933"/></div>
				<div class="lane"><Lane rssOptions={farRight} title="Right" bgcolor="#ffadb633"/></div>
			</div>
		</div>
	</div>
	<Support />
	<About />
	<Contact />
	<Footer />
</main>

<style>
	.lane {
		max-width: 300px;
		min-width: 200px;
		margin: 0 auto;
	}

	.maincontent {
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
		overflow-y: hidden;
		-webkit-overflow-scrolling: touch;
	}

	h1 {
		color: #111111;
		font-size: 2em;
		font-weight: 10;
	}

	h5 {
		color: #444444;
		font-size: 1em;
		font-weight: 5;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>
