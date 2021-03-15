<script>
    export let article;
</script>
<main>
    <div>
        <hr>
        <!-- <img src={article.media_content[0].url} alt="ohno" height="100"> -->
        <a href={article.link}>{@html article.title}</a>
    </div>
</main>

<style>
    hr {
        border: 0;
        color: #dddddd;
        background-color: #dddddd;
        height: 2px;
    }
</style>