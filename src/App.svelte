<script>
	import Lane from "./Lane.svelte";
	import About from "./About.svelte";
	import Contact from "./Contact.svelte";
	import Footer from "./Footer.svelte";
	import Header from "./Header.svelte";
	import Support from "./Support.svelte";
	import debounce from "lodash/debounce";

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

	let current = "";

	const handleScroll = debounce(
		(e) => updateCurrent(e.target.scrollLeft),
		100
	);

	function updateCurrent(scroll_from_left) {
		if (scroll_from_left < 300) {
			current = "left";
		} else if (scroll_from_left < 500) {
			current = "left-lean";
		} else if (scroll_from_left < 1000) {
			current = "center";
		} else if (scroll_from_left < 1500) {
			current = "right-lean";
		} else {
			current = "right";
		}
	}
</script>

<main>
	<div class="maincontent">
		<Header />
		<h1>Pop the Bubble News</h1>
		<h5>
			A simple RSS feed dashboard to quickly view the full spectrum of
			news in the U.S.
		</h5>
		<div class="anchor-nav">
			<a
				class={current === "left" ? "selected lane-nav" : "lane-nav"}
				href="#left"
				on:click={() => (current = "left")}>Left</a
			>
			<a
				class={current === "left-lean"
					? "selected lane-nav"
					: "lane-nav"}
				href="#left-lean"
				on:click={() => (current = "left-lean")}>Left-lean</a
			>
			<a
				class={current === "center" ? "selected lane-nav" : "lane-nav"}
				href="#center"
				on:click={() => (current = "center")}>Center</a
			>
			<a
				class={current === "right-lean"
					? "selected lane-nav"
					: "lane-nav"}
				href="#right-lean"
				on:click={() => (current = "right-lean")}>Right-lean</a
			>
			<a
				class={current === "right" ? "selected lane-nav" : "lane-nav"}
				href="#right"
				on:click={() => (current = "right")}>Right</a
			>
		</div>
		<div class="scrolling-wrapper" on:scroll={handleScroll}>
			<div class="lanes">
				<div id="left" class="lane">
					<Lane
						class="farleft"
						rssOptions={farLeft}
						title="Left"
						bgcolor="#99aeff33"
					/>
				</div>
				<div id="left-lean" class="lane">
					<Lane
						rssOptions={left}
						title="Left-leaning"
						bgcolor="#cce1ff33"
					/>
				</div>
				<div id="center" class="lane">
					<Lane rssOptions={center} title="Center" />
				</div>
				<div id="right-lean" class="lane">
					<Lane
						rssOptions={right}
						title="Right-leaning"
						bgcolor="#ffe0e933"
					/>
				</div>
				<div id="right" class="lane">
					<Lane
						rssOptions={farRight}
						title="Right"
						bgcolor="#ffadb633"
					/>
				</div>
			</div>
		</div>
	</div>
	<Support />
	<About />
	<Contact />
	<Footer />
</main>

<style>
	.selected {
		text-decoration: underline !important;
	}

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

	.anchor-nav {
		display: flex;
		position: relative;
		z-index: 10;
		visibility: hidden;
	}

	@media screen and (max-width: 650px) {
		.scrolling-wrapper {
			overflow-x: auto;
			scroll-snap-type: x mandatory;
			scroll-behavior: smooth;
			margin-top: -15px;
			z-index: 1;
		}

		.lane {
			scroll-snap-align: start;
			flex-shrink: 0;
			margin-right: 100px;
			transform-origin: center center;
			transform: scale(1);
			transition: transform 0.5s;
			position: relative;
			width: 98%;
			max-width: 98%;
			padding-top: 2em;
			margin-top: -2em;
		}

		.lane-nav {
			visibility: visible;
			height: 1.5rem;
			color: #444444;
			text-decoration: none;
			position: relative;
			margin: auto;
		}
		.lane-nav:focus {
			text-decoration: underline;
		}
		.anchor-nav {
			visibility: visible;
		}
	}

	@media (min-width: 650px) {
		main {
			max-width: none;
		}
	}

	/* Don't need button navigation */
	@supports (scroll-snap-type) {
		.lane-nav {
			display: none;
		}
	}
</style>
