<script>
    export let article;
</script>
<main>
    <div>
        <hr>
        <a href={article.link} target="_blank" rel="noopener noreferrer">{@html article.title}</a>
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