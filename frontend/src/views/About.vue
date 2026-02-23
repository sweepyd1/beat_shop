<template>
  <div class="about">
    <h1>О нас</h1>
    <div class="about-content">
      <p>
        BeatMarket — это маркетплейс, где музыканты могут продавать свои биты напрямую покупателям.
        Мы создали платформу, чтобы упростить процесс поиска и приобретения качественных инструменталов.
      </p>
      <p>
        Наша миссия — поддержать независимых продюсеров и дать им возможность монетизировать своё творчество,
        а покупателям — доступ к эксклюзивному контенту по честным ценам.
      </p>

      <h2>Наши преимущества</h2>
      <ul>
        <li>✔️ Прямые продажи без посредников</li>
        <li>✔️ Прозрачные лицензии</li>
        <li>✔️ Удобный поиск и фильтры</li>
        <li>✔️ Высокое качество аудио</li>
        <li>✔️ Поддержка авторов</li>
      </ul>

      <h2>Команда</h2>
      <div class="team">
        <div class="member">
          <img src="https://picsum.photos/100/100?random=201" alt="" />
          <h4>Иван Иванов</h4>
          <p>Основатель, разработчик</p>
        </div>
        <div class="member">
          <img src="https://picsum.photos/100/100?random=202" alt="" />
          <h4>Мария Петрова</h4>
          <p>Дизайнер</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 2rem;
}

.about-content {
  background: rgba(255,255,255,0.02);
  border-radius: 20px;
  padding: 2rem;
  line-height: 1.6;
}

.about-content p {
  margin-bottom: 1rem;
  color: #a0a0a0;
}

.about-content h2 {
  margin: 2rem 0 1rem;
  font-size: 1.5rem;
}

.about-content ul {
  list-style: none;
  padding: 0;
}

.about-content li {
  margin-bottom: 0.5rem;
  color: #a0a0a0;
}

.team {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}

.member {
  text-align: center;
}

.member img {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 0.5rem;
  border: 2px solid #a855f7;
}

.member h4 {
  font-size: 1.1rem;
}

.member p {
  font-size: 0.9rem;
  color: #a0a0a0;
}
</style>