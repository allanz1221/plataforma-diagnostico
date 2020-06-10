-- Documents category
INSERT INTO public.documents_category (id, created_at, updated_at, disabled, name, description) VALUES (1, '2019-05-13 19:42:05.760646', '2019-05-13 19:42:05.760828', false, 'Acta de nacimiento', 'Tu acta de nacimiento');
INSERT INTO public.documents_category (id, created_at, updated_at, disabled, name, description) VALUES (2, '2019-05-13 19:42:29.725222', '2019-05-13 19:42:29.725872', false, 'Certificado de preparatoria', 'Puede ser un kardex, carta de terminación de estudios, etc.');
INSERT INTO public.documents_category (id, created_at, updated_at, disabled, name, description) VALUES (3, '2019-05-13 19:42:40.102187', '2019-05-13 19:42:40.102310', false, 'Copia de la CURP', 'Copia digital de tu CURP');

-- Frequently Asked Questions
INSERT INTO public.core_faqitem (id, created_at, updated_at, disabled, question, answer) VALUES (1, '2019-05-23 19:40:40.016003', '2019-05-23 19:40:40.016046', false, '¿Dónde puedo encontrar la guía del examen?', 'La guía del examen puede descargarse haciendo <a href="/diagnostico/static/files/guia_examen_ues_virtual.pdf" target=_blank>aquí</a>.');
INSERT INTO public.core_faqitem (id, created_at, updated_at, disabled, question, answer) VALUES (2, '2019-05-23 19:43:03.559878', '2019-05-23 19:43:03.559907', false, 'Mi examen se cerró, ¿qué debo de hacer?', 'Si consideras que se cerró tu examen por un error, manda un correo a <a href="mailto:uesvirtual@ues.mx">uesvirtual@ues.mx</a> indicando tu problema.');
INSERT INTO public.core_faqitem (id, created_at, updated_at, disabled, question, answer) VALUES (3, '2019-05-23 19:53:44.260047', '2019-05-23 19:53:44.260076', false, 'No puedo tomarme una foto desde la página, ¿qué puedo hacer?', 'Si no tienes cámara web, o tu sistema no permite tomarte una foto, puedes subir una foto que ya tengas desde la misma sección (donde dice "Subir foto"). En caso de que sigas con problemas, puedes hacérnosla llegar por correo y la subiremos por ti.');
INSERT INTO public.core_faqitem (id, created_at, updated_at, disabled, question, answer) VALUES (4, '2019-05-23 19:57:17.236768', '2019-05-23 19:57:17.236800', false, '¿Cómo debe ser la foto?', 'La foto que te tomes, o subas, debe tener las siguientes características:
<ul>
<li>Estar sobre un fondo blanco</li>
<li>No tener lentes.</li>
<li>Tener las orejas descubiertas.</li>
<li>Tiene que estar lo más clara posible (trata de tomarte la foto en un lugar bien iluminado).</li>
</ul>
En caso de que no cumpla con las características, <strong>será rechazada</strong>, y se te pedirá que nos envíes una nueva.');
INSERT INTO public.core_faqitem (id, created_at, updated_at, disabled, question, answer) VALUES (5, '2019-05-23 20:14:30.740310', '2019-05-23 20:14:30.740376', false, 'Ya terminé mi examen, ¿qué hago ahora?', 'Si ya terminaste de <a href="/diagnostico/exam/">contestar el examen</a>, de subir toda tu <a href="/diagnostico/documents/">documentación</a>, y de proporcionar tus datos para la <a href="/diagnostico/student_card/">credencial</a>, lo que sigue es <strong>esperar a que te contactemos</strong> por correo.');

-- Update indexes
SELECT setval('documents_category_id_seq', (SELECT MAX(id) FROM documents_category)+1);
SELECT setval('core_faqitem_id_seq', (SELECT MAX(id) FROM core_faqitem)+1);
